# Model Context Protocol (MCP): Standardizing AI Tool Use

The Model Context Protocol (MCP) is an open protocol developed by Anthropic that standardizes how AI language models interact with external tools, data sources, and services. It provides a universal interface layer that allows AI systems to be integrated with databases, APIs, file systems, and development tools without custom integration code for each combination.

## Core Architecture

MCP follows a client-server architecture:

- **MCP Client**: The AI application or assistant (e.g., Claude Desktop, an agent application)
- **MCP Server**: A process that exposes tools, resources, or prompts via the MCP protocol
- **Transport**: Communication between client and server via stdio (subprocess), HTTP/SSE, or WebSocket

```
AI Application (Claude/Agent)
    ↓ requests tools, resources
MCP Client Library
    ↓ JSON-RPC over stdio/HTTP
MCP Server
    ↓ executes
Local files / Databases / APIs / External services
```

## MCP Primitives

### Tools

Tools are functions the AI model can invoke:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the product database by query string. Returns matching products."""
    return db.search(query, limit=limit)

@mcp.tool()
async def fetch_weather(city: str) -> dict:
    """Get current weather conditions for a city."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://weather-api.com/{city}")
        return response.json()

mcp.run(transport="stdio")
```

### Resources

Resources are data sources the AI can read:

```python
@mcp.resource("file:///{path}")
def read_file(path: str) -> str:
    """Read a file from the local filesystem."""
    return Path(path).read_text()

@mcp.resource("db://users/{user_id}")
def get_user(user_id: str) -> dict:
    """Get user record from database."""
    return db.users.get(user_id)
```

### Prompts

Reusable prompt templates:

```python
@mcp.prompt()
def code_review_prompt(code: str, language: str) -> str:
    """Generate a code review prompt."""
    return f"Review this {language} code for bugs, security issues, and style:\n\n{code}"
```

## Transport Modes

**stdio transport**: Client spawns server as subprocess; communicates via stdin/stdout. Best for local tools (file system access, database connections).

**HTTP+SSE transport**: Server runs as HTTP service; client connects via Server-Sent Events for streaming. Best for remote services, multiple clients.

## The S7 Agent's Use of MCP

In the Session 7 agent:

1. `agent7.py` starts the MCP server subprocess: `python mcp_server.py`
2. The agent uses `mcp.ClientSession` to connect via stdio
3. Available tools are discovered with `session.list_tools()`
4. The Decision layer selects tools; Action calls them: `session.call_tool(name, args)`

This architecture strictly separates:
- **What the agent intends** (Decision layer, no MCP tool names)
- **What tools exist** (MCP server tool docstrings only)
- **How tools execute** (Action layer, MCP runtime)

## Benefits Over Direct Function Calls

- **Composability**: One AI system can connect to many MCP servers
- **Security**: Server enforces sandboxing (path validation, rate limits)
- **Discoverability**: Tools self-describe via schema
- **Language agnostic**: Server can be any language that speaks JSON-RPC
- **Standardization**: Same client code works with any compliant server

## MCP vs OpenAI Function Calling

| Feature | OpenAI Functions | MCP |
|---------|-----------------|-----|
| Transport | HTTP API | stdio/HTTP/WebSocket |
| Tool schema | JSON Schema | JSON Schema |
| Multi-server | No | Yes |
| Resources | No | Yes (URIs) |
| Prompts | No | Yes |
| Open protocol | No | Yes |
