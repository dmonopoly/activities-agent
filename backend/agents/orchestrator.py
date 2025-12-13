"""Agent orchestrator - Main agent with LLM and tool calling"""
import json
import os
import sys

from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat import ChatCompletion

from agents.tools.scraper import scrape_activities, TOOL_DEFINITION as SCRAPER_TOOL
from agents.tools.sheets import save_to_sheets, TOOL_DEFINITION as SHEETS_TOOL
from agents.tools.preferences import (
    get_user_preferences,
    update_user_preferences,
    TOOL_DEFINITIONS as PREFERENCES_TOOLS
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is required")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

# Register all tools
ALL_TOOLS = [
    SCRAPER_TOOL,
    SHEETS_TOOL,
    *PREFERENCES_TOOLS
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "scrape_activities": scrape_activities,
    "save_to_sheets": save_to_sheets,
    "get_user_preferences": get_user_preferences,
    "update_user_preferences": update_user_preferences,
}

# System prompt
SYSTEM_PROMPT = """You are a helpful assistant that discovers fun activities and date ideas personalized to each user's preferences.

Your capabilities:
1. Search for activities using scrape_activities tool
2. Save activities to Google Sheets using save_to_sheets tool
3. Get and update user preferences using preference tools

When a user asks for activities:
- First check their preferences using get_user_preferences
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
    
    def process_message(self, message: str, model: str = "openai/gpt-4o-mini") -> Dict[str, Any]:
        """
        Process a user message and return agent response
        
        Args:
            message: User's message
            model: Model to use (OpenRouter format)
            
        Returns:
            Dictionary with response and any tool results
        """
        self.conversation_history.append({"role": "user", "content": message})
        print(f"[DEBUG][process_message] Conversation history length incremented to {len(self.conversation_history)}")

        max_iterations = 5
        iteration = 0
        all_tool_results = []  # Accumulate tool results across all iterations
        
        while iteration < max_iterations:
            print('DEBUG][process_message] Iteration', iteration)
            print('DEBUG][process_message] Conversation history', self.conversation_history)
            iteration += 1
            
            response: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                tools=ALL_TOOLS,
                tool_choice="auto"
            )

            print('DEBUG][process_message] response', response)
            message_response = response.choices[0].message
            
            assistant_message = {
                "role": "assistant",
                "content": message_response.content
            }
            # Only include tool_calls if they exist (API doesn't allow empty arrays)
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
                return {
                    "response": message_response.content,
                    "tool_results": all_tool_results
                }
            
            # Execute tool calls
            for tool_call in message_response.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except:
                    arguments = {}
                
                print(f'DEBUG][process_message] Executing tool {tool_name} with args {arguments}')
                result = self._execute_tool(tool_name, arguments)

                print('DEBUG][process_message] Got tool result', result)
                tool_result_entry = {
                    "tool": tool_name,
                    "result": result
                }
                all_tool_results.append(tool_result_entry)
                
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
