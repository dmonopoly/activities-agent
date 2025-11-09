"""Agent orchestrator - Main agent with LLM and tool calling"""
from typing import List, Dict, Any
from openai import OpenAI
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# This ensures env vars are available when this module is imported
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import tools
try:
    from agents.tools.scraper import scrape_activities, TOOL_DEFINITION as SCRAPER_TOOL
    from agents.tools.sheets import save_to_sheets, TOOL_DEFINITION as SHEETS_TOOL
    from agents.tools.preferences import (
        get_user_preferences,
        update_user_preferences,
        TOOL_DEFINITIONS as PREFERENCES_TOOLS
    )
except ImportError as e:
    # Fallback for when running from different directory
    import importlib.util
    scraper_path = Path(__file__).parent / "tools" / "scraper.py"
    sheets_path = Path(__file__).parent / "tools" / "sheets.py"
    prefs_path = Path(__file__).parent / "tools" / "preferences.py"
    
    def load_module(path):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    scraper_module = load_module(scraper_path)
    sheets_module = load_module(sheets_path)
    prefs_module = load_module(prefs_path)
    
    scrape_activities = scraper_module.scrape_activities
    SCRAPER_TOOL = scraper_module.TOOL_DEFINITION
    save_to_sheets = sheets_module.save_to_sheets
    SHEETS_TOOL = sheets_module.TOOL_DEFINITION
    get_user_preferences = prefs_module.get_user_preferences
    update_user_preferences = prefs_module.update_user_preferences
    PREFERENCES_TOOLS = prefs_module.TOOL_DEFINITIONS

# Initialize OpenAI client (works with OpenRouter)
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
        """Execute a tool function"""
        if tool_name not in TOOL_FUNCTIONS:
            return {"error": f"Unknown tool: {tool_name}"}
        
        func = TOOL_FUNCTIONS[tool_name]
        
        # Handle user_id injection for preference tools
        if tool_name in ["get_user_preferences", "update_user_preferences"]:
            if "user_id" not in arguments:
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
        # Add user message to conversation
        self.conversation_history.append({"role": "user", "content": message})
        
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                tools=ALL_TOOLS,
                tool_choice="auto"
            )
            
            message_response = response.choices[0].message
            
            # Add assistant message to history
            self.conversation_history.append({
                "role": "assistant",
                "content": message_response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in (message_response.tool_calls or [])
                ]
            })
            
            # If no tool calls, return the response
            if not message_response.tool_calls:
                return {
                    "response": message_response.content,
                    "tool_results": []
                }
            
            # Execute tool calls
            tool_results = []
            for tool_call in message_response.tool_calls:
                tool_name = tool_call.function.name
                import json
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except:
                    arguments = {}
                
                result = self._execute_tool(tool_name, arguments)
                
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
                
                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
            # Continue loop to let LLM process tool results
        
        # If we hit max iterations, return last response
        return {
            "response": self.conversation_history[-1].get("content", "I encountered an issue processing your request."),
            "tool_results": tool_results
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
