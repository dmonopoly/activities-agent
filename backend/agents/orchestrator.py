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
    MOCK_RESPONSES_NO_TOOLS,
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = "xiaomi/mimo-v2-flash:free"
# OPENROUTER_DEFAULT_MODEL = "openai/gpt-4o-mini"

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
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        # Mock state (reset per message)
        self._mock_iteration = 0
        self._mock_scenario: Dict[str, Any] = {}
    
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
        return client.chat.completions.create(
            model=model,
            messages=self.conversation_history,
            tools=ALL_TOOLS,
            tool_choice="auto"
        )
    
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
    
    def process_message(self, message: str, model: str = OPENROUTER_DEFAULT_MODEL) -> Dict[str, Any]:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's message
            model: Model to use (OpenRouter format)
            
        Returns:
            Dictionary with response and any tool results
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
        
        while iteration < max_iterations:
            iteration += 1
            print(f'[ORCHESTRATOR] Iteration {iteration}/{max_iterations}')
            
            response = self._get_completion(model)
            message_response = response.choices[0].message
            print(f"[ORCHESTRATOR] Response received, has_tool_calls={bool(message_response.tool_calls)}")
            
            assistant_message = {
                "role": "assistant",
                "content": message_response.content
            }
            if message_response.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message_response.tool_calls
                ]
            self.conversation_history.append(assistant_message)
            
            if not message_response.tool_calls:
                print(f"[ORCHESTRATOR] No tool calls, returning final response")
                return {
                    "response": message_response.content,
                    "tool_results": all_tool_results
                }
            
            # Execute tool calls
            print(f"[ORCHESTRATOR] Executing {len(message_response.tool_calls)} tool call(s)")
            for tool_call in message_response.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                print(f'[ORCHESTRATOR] Executing tool: {tool_name} with args: {arguments}')
                result = self._execute_tool(tool_name, arguments)
                print(f'[ORCHESTRATOR] Tool {tool_name} completed')
                
                all_tool_results.append({"tool": tool_name, "result": result})
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
        return {
            "response": self.conversation_history[-1].get("content", "I encountered an issue processing your request."),
            "tool_results": all_tool_results
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
