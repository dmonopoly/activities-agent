"""Agent orchestrator - Main agent with LLM and tool calling"""
import json
import os
import random

from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion

from agents.config import ENABLE_OPENROUTER_API
from agents.mock_data import (
    MOCK_RESPONSES_WITH_TOOLS,
    make_mock_completion
)
from agents.tools.google_maps import search_places_for_dates, TOOL_DEFINITION as GOOGLE_MAPS_TOOL
from agents.tools.weather import get_weather_for_location, TOOL_DEFINITION as WEATHER_TOOL
from agents.tools.scraper import scrape_activities, TOOL_DEFINITION as SCRAPER_TOOL
from agents.tools.sheets import save_to_sheets, TOOL_DEFINITION as SHEETS_TOOL
from agents.tools.preferences import (
    get_user_preferences,
    update_user_preferences,
    TOOL_DEFINITIONS as PREFERENCES_TOOLS
)
from agents.available_tools import filter_to_available_tools

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# $$ WARNING: Model choice affects cost. Use free models for now.
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = 'xiaomi/mimo-v2-flash:free'
OPENROUTER_BACKUP_MODEL = 'google/gemini-2.0-flash-exp:free'
# OPENROUTER_DEFAULT_MODEL = 'openai/gpt-4o-mini'

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

ALL_TOOLS = [
    SCRAPER_TOOL,
    SHEETS_TOOL,
    *PREFERENCES_TOOLS,
    GOOGLE_MAPS_TOOL,
    WEATHER_TOOL
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "scrape_activities": scrape_activities,
    "save_to_sheets": save_to_sheets,
    "get_user_preferences": get_user_preferences,
    "update_user_preferences": update_user_preferences,
    "search_places_for_dates": search_places_for_dates,
    "get_weather_for_location": get_weather_for_location,
}

SYSTEM_PROMPT = """You are a helpful assistant that discovers fun activities and date ideas personalized to each user's preferences.

Your capabilities:
1. Search for activities using scrape_activities tool
2. Search for date activities between two locations using search_places_for_dates tool (Google Maps integration)
3. Get weather information using get_weather_for_location tool
4. Save activities to Google Sheets using save_to_sheets tool
5. Get and update user preferences using preference tools

When a user asks for activities:
- First check their preferences using get_user_preferences
- If they mention two locations (e.g., "between X and Y"), use search_places_for_dates to find places between those locations
- For outdoor activities, consider checking weather using get_weather_for_location
- Use those preferences to search for relevant activities
- Present activities in a friendly, engaging way
- Offer to save activities to a spreadsheet when appropriate

Be conversational, helpful, and proactive in suggesting activities based on user preferences."""


class AgentOrchestrator:
    """Orchestrates LLM agent with tool calling"""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.reset_conversation()
        
        # Mock state (reset per message)
        self._mock_iteration = 0
        self._mock_scenario: Dict[str, Any] = {}
    
    def _build_preferences_context(self, prefs: Dict[str, Any]) -> str:
        """Build a context message from user preferences."""
        location = prefs.get('location') or 'not specified'
        interests = prefs.get('interests') or []
        budget_min = prefs.get('budget_min')
        budget_max = prefs.get('budget_max')
        
        # Format budget range
        if budget_min is not None and budget_max is not None:
            budget = f"${budget_min}-${budget_max}"
        elif budget_min is not None:
            budget = f"${budget_min}+"
        elif budget_max is not None:
            budget = f"up to ${budget_max}"
        else:
            budget = "not specified"
        
        # Format interests
        interests_str = ", ".join(interests) if interests else "not specified"
        
        return (
            f"Current user preferences:\n"
            f"- Location: {location}\n"
            f"- Interests: {interests_str}\n"
            f"- Budget: {budget}\n"
            f"\nUse these preferences to personalize activity recommendations. "
            f"You do not need to call get_user_preferences unless the user asks to change or view their preferences."
        )
    
    def _get_completion(self, model: str) -> ChatCompletion:
        """
        Get a chat completion from the LLM (or mock if API disabled).
        
        In mock mode:
        - Iteration 1: Returns ChatCompletion with tool_calls (if scenario has tools)
        - Iteration 2+: Returns ChatCompletion with final content
        """
        if not ENABLE_OPENROUTER_API:
            self._mock_iteration += 1
            scenario = self._mock_scenario
            tool_calls = scenario.get("tool_calls", [])
            
            if self._mock_iteration == 1 and tool_calls:
                # First iteration with tools: return tool calls
                print(f"[ORCHESTRATOR] ❌ API DISABLED - returning MOCK tool calls")
                print(f"[ORCHESTRATOR] Mock tools: {[tc['name'] for tc in tool_calls]}")
                return make_mock_completion(tool_calls=tool_calls)
            else:
                # Final iteration: return response content
                content = scenario.get("response", "Mock response")
                print(f"[ORCHESTRATOR] ❌ API DISABLED - returning MOCK final response")
                print(f"[ORCHESTRATOR] Mock response preview: {content[:80]}...")
                return make_mock_completion(content=content)
        
        print(f"[ORCHESTRATOR] ✅ API ENABLED - calling OpenRouter API with model={model}")
        try:
            response = client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                tools=ALL_TOOLS,
                tool_choice="auto"
            )
            print(f"[ORCHESTRATOR] ✅ HISTORY: {self.conversation_history}")
            print(f"[ORCHESTRATOR] ✅ API RESPONSE: {response}")
            return response
        except Exception as e:
            print(f"[ORCHESTRATOR] ❌ API ERROR: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'status_code') and e.response.status_code == 429:
                print(f"[ORCHESTRATOR] ❌ RATE LIMIT ERROR - Retrying with backup model")
                return self._get_completion(OPENROUTER_BACKUP_MODEL)
            raise
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool function with automatic context injection based on tool definition"""
        if tool_name not in TOOL_FUNCTIONS:
            return {"error": f"Unknown tool: {tool_name}"}
        
        func = TOOL_FUNCTIONS[tool_name]
        
        # Check tool definition to see if user_id is required and inject if missing
        tool_def = next(
            (t for t in ALL_TOOLS if t.get("function", {}).get("name") == tool_name),
            None
        )
        if tool_def:
            required_params = tool_def.get("function", {}).get("parameters", {}).get("required", [])
            if "user_id" in required_params:
                # Always override user_id for preference tools to ensure consistency
                arguments["user_id"] = self.user_id
        
        try:
            result = func(**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def _build_skipped_tools_message(self, skipped_tools: List[str]) -> str:
        """Build a playful message about skipped tools."""
        if not skipped_tools:
            return None
        tools_str = " and ".join(skipped_tools) if len(skipped_tools) <= 2 else \
            ", ".join(skipped_tools[:-1]) + f", and {skipped_tools[-1]}"
        return f"I wanted to use {tools_str}, but the website owner has disabled them unless you know the magic word."
    
    def process_message(self, message: str, model: str = OPENROUTER_DEFAULT_MODEL) -> Dict[str, Any]:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's message
            model: Model to use (OpenRouter format)
            
        Returns:
            Dictionary with response, tool_results, and skipped_tools_message (if any)
        """
        self.conversation_history.append({"role": "user", "content": message})
        
        print(f"[ORCHESTRATOR] process_message called with message: {message[:100]}")
        print(f"[ORCHESTRATOR] ENABLE_OPENROUTER_API={ENABLE_OPENROUTER_API}")
        print(f"[ORCHESTRATOR] Conversation history length: {len(self.conversation_history)}")

        # Reset mock state and select scenario for this message
        self._mock_iteration = 0
        if not ENABLE_OPENROUTER_API:
            self._mock_scenario = random.choice(MOCK_RESPONSES_WITH_TOOLS)

        max_iterations = 3
        iteration = 0
        all_tool_results = []
        all_skipped_tools: List[str] = []
        
        while iteration < max_iterations:
            iteration += 1
            print(f'[ORCHESTRATOR] Iteration {iteration}/{max_iterations}')
            
            response = self._get_completion(model)
            
            if not response.choices:
                print(f"[ORCHESTRATOR] ❌ ERROR: Empty choices in API response")
                return {
                    "response": "I encountered an issue processing your request. Please try again.",
                    "tool_results": all_tool_results,
                    "skipped_tools_message": None
                }
            
            message_response = response.choices[0].message
            content = message_response.content or ""  # Handle None content
            print(f"[ORCHESTRATOR] Response received, has_tool_calls={bool(message_response.tool_calls)}, content_len={len(content)}")
            
            assistant_message: Dict[str, Any] = {
                "role": "assistant",
                "content": content
            }
            
            # Filter tool calls and track skipped ones
            skipped_tools: List[str] = []
            if message_response.tool_calls:
                filtered_tools, skipped_tools = filter_to_available_tools(message_response.tool_calls)
                if filtered_tools:
                    assistant_message["tool_calls"] = filtered_tools
                for tool_name in skipped_tools:
                    if tool_name not in all_skipped_tools:
                        all_skipped_tools.append(tool_name)
            
            self.conversation_history.append(assistant_message)
            
            # Check if we have any tools to execute
            has_tools_to_execute = "tool_calls" in assistant_message and assistant_message["tool_calls"]
            
            if not has_tools_to_execute:
                # No tools to execute - either LLM gave final response, or all tools were filtered
                if skipped_tools and not content:
                    # All tools were skipped and LLM didn't provide content
                    # Inject a hint and get a text response
                    print(f"[ORCHESTRATOR] All tools skipped ({skipped_tools}), requesting fallback response")
                    hint = (
                        f"The tools you requested ({', '.join(skipped_tools)}) are currently unavailable. "
                        "Please provide a helpful response without using those tools, "
                        "based on your general knowledge."
                    )
                    self.conversation_history.append({"role": "system", "content": hint})
                    
                    fallback_response = self._get_completion(model)
                    if not fallback_response.choices:
                        fallback_content = "I'm having trouble processing your request."
                    else:
                        fallback_content = fallback_response.choices[0].message.content or ""
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": fallback_content
                    })
                    
                    skipped_tools_msg = self._build_skipped_tools_message(all_skipped_tools)
                    fallback_content += "\n\n(Note:" + skipped_tools_msg + ")" if skipped_tools_msg else ""
                    return {
                        "response": fallback_content.strip() or "I couldn't generate a response.",
                        "tool_results": all_tool_results,
                        "skipped_tools_message": skipped_tools_msg
                    }
                
                print(f"[ORCHESTRATOR] No tool calls, returning final response")
                final_msg = content if content else ""
                final_msg += " " + skipped_tools_msg if skipped_tools_msg else ""
                return {
                    "response": final_msg.strip() or "I couldn't generate a response.",
                    "tool_results": all_tool_results,
                    "skipped_tools_message": self._build_skipped_tools_message(all_skipped_tools) if all_skipped_tools else None
                }
            
            num_tool_calls = len(assistant_message["tool_calls"])
            print(f'[ORCHESTRATOR] Executing {num_tool_calls} tool call(s)')
            for tool_call in assistant_message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    arguments = {}
                
                print(f'[ORCHESTRATOR] Executing tool: {tool_name} with args: {arguments}')
                result = self._execute_tool(tool_name, arguments)
                print(f'[ORCHESTRATOR] Tool {tool_name} completed')
                
                all_tool_results.append({"tool": tool_name, "result": result})
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result)
                })
        
        # If we exit the loop with tool results but no final response, 
        # make one more LLM call to generate a human-readable summary
        print(f"[ORCHESTRATOR] Max iterations reached, generating final summary response")
        summary_response = self._get_completion(model)
        if summary_response and summary_response.choices:
            summary_content = summary_response.choices[0].message.content or ""
            self.conversation_history.append({
                "role": "assistant",
                "content": summary_content
            })
            return {
                "response": summary_content or "I found some results but couldn't summarize them.",
                "tool_results": all_tool_results,
                "skipped_tools_message": self._build_skipped_tools_message(all_skipped_tools) if all_skipped_tools else None
            }
        
        return {
            "response": "I encountered an issue processing your request.",
            "tool_results": all_tool_results,
            "skipped_tools_message": self._build_skipped_tools_message(all_skipped_tools) if all_skipped_tools else None
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        prefs = get_user_preferences(self.user_id)
        prefs_context = self._build_preferences_context(prefs)
        
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": prefs_context}
        ]
