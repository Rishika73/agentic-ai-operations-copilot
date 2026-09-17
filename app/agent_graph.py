from typing import Dict, Any

from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.llm import generate_operational_answer
from app.actions import propose_action

from tools.crm_tool import (
    get_at_risk_accounts,
    get_accounts_renewing_within,
)
from tools.ticket_tool import get_open_incidents
from tools.knowledge_tool import search_knowledge


def route_query(state: AgentState) -> Dict[str, Any]:
    query = state["user_query"].lower()

    if (
        "policy" in query
        or "procedure" in query
        or "guideline" in query
        or "how should" in query
    ):
        route = "knowledge"

    elif "risk" in query or "renew" in query:
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


def synthesis_node(state: AgentState) -> Dict[str, Any]:
    answer = generate_operational_answer(
        user_query=state["user_query"],
        route=state["route"],
        tool_results=state.get("tool_results", []),
        retrieved_context=state.get("retrieved_context", []),
    )

    return {
        "final_answer": answer
    }


def choose_route(state: AgentState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", route_query)
    graph.add_node("account_risk", account_risk_node)
    graph.add_node("incident", incident_node)
    graph.add_node("knowledge", knowledge_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("action_proposal", propose_action)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        choose_route,
        {
            "account_risk": "account_risk",
            "incident": "incident",
            "knowledge": "knowledge",
        },
    )

    graph.add_edge("account_risk", "synthesis")
    graph.add_edge("incident", "synthesis")
    graph.add_edge("knowledge", "synthesis")

    graph.add_edge("synthesis", "action_proposal")
    graph.add_edge("action_proposal", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent(query: str):
    return agent_graph.invoke(
        {
            "user_query": query
        }
    )


if __name__ == "__main__":
    questions = [
        "Which customer accounts are at risk?",
        "What open incidents do we have?",
        "What is the policy for critical incident response?",
    ]

    for question in questions:
        print("\n" + "=" * 70)

        print("\nQUESTION")
        print(question)

        result = run_agent(question)

        print("\nRESULT")
        print(result["final_answer"])

        print("\nPROPOSED ACTION")
        print(result.get("proposed_action"))

        print("\nAPPROVAL REQUIRED")
        print(result.get("requires_approval"))

        print("\nAPPROVAL STATUS")
        print(result.get("approval_status"))
