import sqlite3
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from app.state import AgentState
from app.actions import (
    propose_action,
    human_approval_node,
    execute_action,
)

from agents.incident_agent import run_incident_agent
from agents.account_risk_agent import run_account_risk_agent
from agents.knowledge_agent import run_knowledge_agent


# ---------------------------------------------------------
# Router
# ---------------------------------------------------------

def router_node(state: AgentState) -> Dict[str, Any]:
    query = state.get("user_query", "").lower()

    incident_keywords = [
        "incident",
        "incidents",
        "outage",
        "error",
        "errors",
        "failure",
        "failures",
        "ticket",
        "tickets",
        "critical issue",
    ]

    account_risk_keywords = [
        "account",
        "accounts",
        "customer risk",
        "at risk",
        "renewal",
        "renewals",
        "health score",
        "customer health",
        "retention",
    ]

    if any(keyword in query for keyword in incident_keywords):
        route = "incident"

    elif any(keyword in query for keyword in account_risk_keywords):
        route = "account_risk"

    else:
        route = "knowledge"

    return {
        "route": route,
    }


# ---------------------------------------------------------
# Specialized agent nodes
# ---------------------------------------------------------

def incident_node(state: AgentState) -> Dict[str, Any]:
    result = run_incident_agent(
        state["user_query"]
    )

    return {
        "tool_results": result.get(
            "tool_results",
            [],
        ),
        "final_answer": result.get(
            "answer",
            "",
        ),
    }


def account_risk_node(state: AgentState) -> Dict[str, Any]:
    result = run_account_risk_agent(
        state["user_query"]
    )

    return {
        "tool_results": result.get(
            "tool_results",
            [],
        ),
        "final_answer": result.get(
            "answer",
            "",
        ),
    }


def knowledge_node(state: AgentState) -> Dict[str, Any]:
    result = run_knowledge_agent(
        state["user_query"]
    )

    return {
        "retrieved_context": result.get(
            "retrieved_context",
            [],
        ),
        "final_answer": result.get(
            "answer",
            "",
        ),
    }


# ---------------------------------------------------------
# Route selector
# ---------------------------------------------------------

def select_route(state: AgentState) -> str:
    return state.get(
        "route",
        "knowledge",
    )


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node(
        "router",
        router_node,
    )

    graph.add_node(
        "incident",
        incident_node,
    )

    graph.add_node(
        "account_risk",
        account_risk_node,
    )

    graph.add_node(
        "knowledge",
        knowledge_node,
    )

    graph.add_node(
        "action_proposal",
        propose_action,
    )

    graph.add_node(
        "human_approval",
        human_approval_node,
    )

    graph.add_node(
        "execute_action",
        execute_action,
    )

    # Entry point
    graph.set_entry_point(
        "router"
    )

    # Router -> specialized agent
    graph.add_conditional_edges(
        "router",
        select_route,
        {
            "incident": "incident",
            "account_risk": "account_risk",
            "knowledge": "knowledge",
        },
    )

    # Specialized agents -> action proposal
    graph.add_edge(
        "incident",
        "action_proposal",
    )

    graph.add_edge(
        "account_risk",
        "action_proposal",
    )

    graph.add_edge(
        "knowledge",
        "action_proposal",
    )

    # Action workflow
    graph.add_edge(
        "action_proposal",
        "human_approval",
    )

    graph.add_edge(
        "human_approval",
        "execute_action",
    )

    graph.add_edge(
        "execute_action",
        END,
    )

    # Persistent SQLite checkpoint memory
    sqlite_connection = sqlite3.connect(
        "agent_memory.db",
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(
        sqlite_connection
    )

    return graph.compile(
        checkpointer=checkpointer
    )


# ---------------------------------------------------------
# Graph instance
# ---------------------------------------------------------

agent_graph = build_graph()


# ---------------------------------------------------------
# CLI
# ---------------------------------------------------------

if __name__ == "__main__":

    print(
        "\nAgentic AI Operations Copilot"
    )

    print(
        "-----------------------------"
    )

    user_query = input(
        "\nAsk an operations question: "
    ).strip()

    # Fixed thread ID so LangGraph checkpoints
    # persist between runs.
    thread_id = "demo-operations-thread"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    initial_state = {
        "user_query": user_query,
    }

    result = agent_graph.invoke(
        initial_state,
        config=config,
    )

    print("\nROUTE")
    print(
        result.get(
            "route",
            "unknown",
        )
    )

    print("\nANSWER")
    print(
        result.get(
            "final_answer",
            "No answer generated.",
        )
    )

    print("\nPROPOSED ACTION")
    print(
        result.get(
            "proposed_action"
        )
    )

    print("\nAPPROVAL REQUIRED")
    print(
        result.get(
            "requires_approval",
            False,
        )
    )

    print("\nAPPROVAL STATUS")
    print(
        result.get(
            "approval_status"
        )
    )

    # -----------------------------------------------------
    # Human-in-the-loop approval
    # -----------------------------------------------------

    if "__interrupt__" in result:

        print(
            "\nHuman approval is required."
        )

        decision = input(
            "Approve or reject? "
        ).strip().lower()

        resumed_result = agent_graph.invoke(
            Command(
                resume=decision
            ),
            config=config,
        )

        print(
            "\nFINAL APPROVAL STATUS"
        )

        print(
            resumed_result.get(
                "approval_status"
            )
        )

        print(
            "\nACTION RESULT"
        )

        print(
            resumed_result.get(
                "action_result"
            )
        )

    else:

        print(
            "\nACTION RESULT"
        )

        print(
            result.get(
                "action_result"
            )
        )
