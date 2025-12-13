# Architecture: Merged MCP-style vs Traditional MCP

This document explains the architectural decisions in this project, particularly how the agent orchestrator implements an "MCP-style" merged architecture compared to a traditional MCP (Model Context Protocol) setup.

## What is MCP?

**Model Context Protocol (MCP)** is a standard for connecting LLMs to external tools and data sources. It defines:
- How tools are described (schemas)
- How tool calls are requested and executed
- How results are returned

The key components are:
- **Tool Definitions**: JSON schemas describing what tools do and their parameters
- **Tool Execution**: The mechanism to actually run tools
- **Protocol**: Communication between LLM client and tool server

## Traditional MCP Architecture

In a standard MCP setup, the system is split into separate processes:

```
┌─────────────────┐         MCP Protocol         ┌─────────────────┐
│                 │  ←─────────────────────────→ │                 │
│   MCP Client    │     (stdio/HTTP/WebSocket)   │   MCP Server    │
│  (Orchestrator) │                              │   (Tool Host)   │
│                 │                              │                 │
└─────────────────┘                              └─────────────────┘
        ▲                                                ▲
        │                                                │
        ▼                                                ▼
   ┌─────────┐                                    ┌─────────────┐
   │   LLM   │                                    │   Tools     │
   │   API   │                                    │ (functions) │
   └─────────┘                                    └─────────────┘
```

### MCP Server Responsibilities
- Exposes tool definitions via `tools/list`
- Executes tools via `tools/call`
- Can be written in any language
- Runs as a separate process
- Communicates via standardized protocol

### MCP Client Responsibilities
- Connects to MCP server(s)
- Retrieves tool definitions
- Passes tools to LLM
- Routes LLM tool calls to the MCP server
- Returns results to LLM

### Communication Flow
1. Client requests tool list from server
2. Client passes tool definitions to LLM
3. LLM decides to call a tool
4. Client sends tool call to server
5. Server executes tool
6. Server returns result to client
7. Client passes result back to LLM

## This Project: Merged Architecture

In this project, we use a **merged architecture** where the orchestrator combines both roles:

```
┌───────────────────────────────────────────────────────────┐
│                      AgentOrchestrator                    │
│                                                           │
│  ┌──────────────────┐      ┌──────────────────────────┐   │
│  │  MCP-style       │      │  Tool Execution          │   │
│  │  Tool Schemas    │      │  (direct function calls) │   │
│  │  (ALL_TOOLS)     │      │  (TOOL_FUNCTIONS)        │   │
│  └──────────────────┘      └──────────────────────────┘   │
│           ▲                           ▲                   │
│           │      process_message()    │                   │
│           │            │              │                   │
│           ▼            ▼              ▼                   │
│     ┌──────────────────────────────────────┐              │
│     │  1. Pass tools to LLM                │              │
│     │  2. Get tool calls from LLM          │              │
│     │  3. Execute tools directly           │              │
│     │  4. Return results to LLM            │              │
│     └──────────────────────────────────────┘              │
└───────────────────────────────────────────────────────────┘
                          ▲
                          │
                          ▼
                    ┌───────────┐
                    │  LLM API  │
                    │(OpenRouter)│
                    └───────────┘
```

### How It Works in Code

```python
# Tool definitions (MCP-style schemas)
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

# Combined in one class
class AgentOrchestrator:
    def _execute_tool(self, tool_name, arguments):
        func = TOOL_FUNCTIONS[tool_name]
        return func(**arguments)
    
    def process_message(self, message):
        # Pass ALL_TOOLS to LLM
        response = client.chat.completions.create(
            model=model,
            messages=self.conversation_history,
            tools=ALL_TOOLS,  # MCP-style definitions
        )
        
        # Execute tools directly
        for tool_call in response.tool_calls:
            result = self._execute_tool(tool_name, arguments)
```

## Comparison

| Aspect | Traditional MCP | Merged Architecture |
|--------|-----------------|---------------------|
| **Process Model** | Separate processes | Single process |
| **Communication** | Protocol (stdio/HTTP/WebSocket) | Direct function calls |
| **Tool Language** | Any language | Same as orchestrator |
| **Deployment** | Multiple services | Single service |
| **Complexity** | Higher (IPC, protocol) | Lower (no IPC) |
| **Scalability** | Tools can scale independently | Tools scale with orchestrator |
| **Isolation** | Tools isolated from each other | Tools share process |
| **Debugging** | Harder (multiple processes) | Easier (single process) |
| **Latency** | Higher (network/IPC overhead) | Lower (in-process) |

## When to Use Each

### Use Traditional MCP When:
- Tools are written in different languages
- Tools need isolated execution environments
- Tools are provided by third parties
- You need to scale tools independently
- You want standardized interfaces across multiple systems
- Security requires tool isolation

### Use Merged Architecture When:
- All tools are in the same language (Python in this case)
- Tools are part of your codebase
- Simplicity and ease of debugging are priorities
- Low latency is important
- Single deployment is preferred
- Tools don't need independent scaling

## Why This Project Uses Merged Architecture

1. **All Python**: All tools are Python functions in the same codebase
2. **Simplicity**: No need for inter-process communication
3. **Single Deployment**: Easier to deploy as one FastAPI service
4. **Debugging**: Easier to trace issues in a single process
5. **Learning**: Demonstrates MCP concepts without protocol complexity

## The "MCP-style" Part

Even though we don't use a separate MCP server, we still use **MCP-style tool definitions**:

```python
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "scrape_activities",
        "description": "Search and scrape activities from the web",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for activities"
                },
                # ... more parameters
            },
            "required": ["query"]
        }
    }
}
```

This format is compatible with:
- OpenAI function calling API
- MCP protocol tool definitions
- Other LLM APIs that support function calling

## Evolution Path

If this project needed to evolve to traditional MCP:

1. **Extract tools to MCP server**: Move tool functions and definitions to a separate process
2. **Add MCP protocol layer**: Implement `tools/list` and `tools/call` endpoints
3. **Update orchestrator**: Replace direct function calls with MCP client calls
4. **Deploy separately**: Run MCP server as a separate service

The current MCP-style tool definitions would transfer directly, minimizing refactoring.

## Key Takeaways

1. **MCP is about standardization**: The protocol standardizes how tools are defined and called
2. **Architecture is flexible**: You can implement MCP concepts with or without separate servers
3. **Start simple**: Merged architecture is simpler for single-language, single-team projects
4. **Schema compatibility**: Using MCP-style schemas keeps the door open for future evolution
5. **Trade-offs exist**: Simplicity vs. scalability, ease vs. flexibility

## Further Reading

- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)

