from datetime import datetime

from mcp.server import MCPServer

mcp = MCPServer("study-buddy")


@mcp.tool()
def current_time() -> str:
    """Return the current server time."""
    return datetime.now().isoformat()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")