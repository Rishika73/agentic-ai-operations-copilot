from typing import Dict, Any

from app.state import AgentState
from tools.crm_tool import (
    get_at_risk_accounts,
    get_accounts_renewing_within,
)
from tools.ticket_tool import get_open_incidents
from tools.knowledge_tool import search_knowledge


def route_query(state: AgentState) -> Dict[str, Any]:
    query = state["user_query"].lower()

    if "risk" in query or "renew" in query:
        route = "account_risk"

    elif "incident" in query or "ticket" in query:
        route = "incident"

    else:
        route = "knowledge"

    return {
        "route": route
    }


def account_risk_node(state: AgentState) -> Dict[str, Any]:
    accounts = get_at_risk_accounts()
    renewals = get_accounts_renewing_within(30)

    return {
        "tool_results": [
            {
                "tool": "crm",
                "at_risk_accounts": accounts,
                "renewing_within_30_days": renewals,
            }
        ]
    }


def incident_node(state: AgentState) -> Dict[str, Any]:
    incidents = get_open_incidents()

    return {
        "tool_results": [
            {
                "tool": "support_tickets",
                "open_incidents": incidents,
            }
        ]
    }


def knowledge_node(state: AgentState) -> Dict[str, Any]:
    results = search_knowledge(
        state["user_query"]
    )

    return {
        "retrieved_context": results
    }
