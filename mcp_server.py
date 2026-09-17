from mcp.server import MCPServer

from tools.ticket_tool import get_open_incidents
from tools.crm_tool import (
    get_at_risk_accounts,
    get_accounts_renewing_within,
)
from tools.knowledge_tool import search_knowledge


mcp = MCPServer("agentic-ai-operations-copilot")


@mcp.tool()
def open_incidents():
    """Return all currently open support incidents."""
    return get_open_incidents()


@mcp.tool()
def at_risk_accounts():
    """Return customer accounts currently marked high risk."""
    return get_at_risk_accounts()


@mcp.tool()
def accounts_renewing_within(days: int = 30):
    """Return accounts renewing within the given number of days."""
    return get_accounts_renewing_within(days)


@mcp.tool()
def search_operations_knowledge(query: str):
    """Search the operations knowledge base."""
    return search_knowledge(query)


if __name__ == "__main__":
    mcp.run()