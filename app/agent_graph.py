from typing import Dict, Any
import uuid

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.state import AgentState
from app.llm import generate_operational_answer
from app.actions import (
    propose_action,
    human_approval_node,
    execute_action,
)

from tools.crm_tool import (
    get_at_risk_accounts,
    get_accounts_renewing_within,
)
from tools.ticket_tool import get_open_incidents
from tools.knowledge_tool import search_knowledge


# --------------------------------------------------
# LangGraph checkpointer
# --------------------------------------------------

checkpointer = InMemorySaver()


# --------------------------------------------------
# Router
# --------------------------------------------------

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


# --------------------------------------------------
# Account Risk Tool Node
# --------------------------------------------------

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


# --------------------------------------------------
# Incident Tool Node
# --------------------------------------------------

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


# --------------------------------------------------
# Knowledge Tool Node
# --------------------------------------------------

def knowledge_node(state: AgentState) -> Dict[str, Any]:
    results = search_knowledge(
        state["user_query"]
    )

    return {
        "retrieved_context": results
    }


# --------------------------------------------------
# LLM Synthesis Node
# --------------------------------------------------

def synthesis_node(state: AgentState) -> Dict[str, Any]:
    answer = generate_operational_answer(
        user_query=state["user_query"],
        route=state["route"],
        tool_results=state.get(
            "tool_results",
            [],
        ),
        retrieved_context=state.get(
            "retrieved_context",
            [],
        ),
    )

    return {
        "final_answer": answer
    }


# --------------------------------------------------
# Route Selector
# --------------------------------------------------

def choose_route(state: AgentState) -> str:
    return state["route"]


# --------------------------------------------------
# Build Agent Graph
# --------------------------------------------------

def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node(
        "router",
        route_query,
    )

    graph.add_node(
        "account_risk",
        account_risk_node,
    )

    graph.add_node(
        "incident",
        incident_node,
    )

    graph.add_node(
        "knowledge",
        knowledge_node,
    )

    graph.add_node(
        "synthesis",
        synthesis_node,
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

    # Routing
    graph.add_conditional_edges(
        "router",
        choose_route,
        {
            "account_risk": "account_risk",
            "incident": "incident",
            "knowledge": "knowledge",
        },
    )

    # Tool results -> LLM
    graph.add_edge(
        "account_risk",
        "synthesis",
    )

    graph.add_edge(
        "incident",
        "synthesis",
    )

    graph.add_edge(
        "knowledge",
        "synthesis",
    )

    # LLM -> proposed action
    graph.add_edge(
        "synthesis",
        "action_proposal",
    )

    # Proposed action -> human approval
    graph.add_edge(
        "action_proposal",
        "human_approval",
    )

    # Human decision -> execution node
    graph.add_edge(
        "human_approval",
        "execute_action",
    )

    # Execution -> end
    graph.add_edge(
        "execute_action",
        END,
    )

    return graph.compile(
        checkpointer=checkpointer
    )


agent_graph = build_graph()


# --------------------------------------------------
# Start Agent
# --------------------------------------------------

def run_agent(
    query: str,
    thread_id: str,
):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return agent_graph.invoke(
        {
            "user_query": query
        },
        config=config,
    )


# --------------------------------------------------
# Resume Agent After Human Decision
# --------------------------------------------------

def resume_agent(
    decision: str,
    thread_id: str,
):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return agent_graph.invoke(
        Command(
            resume=decision
        ),
        config=config,
    )


# --------------------------------------------------
# CLI Demo
# --------------------------------------------------

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

        # Each question gets its own persistent graph thread.
        thread_id = str(
            uuid.uuid4()
        )

        result = run_agent(
            question,
            thread_id,
        )

        print("\nRESULT")
        print(
            result.get(
                "final_answer"
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
                "requires_approval"
            )
        )

        print("\nAPPROVAL STATUS")
        print(
            result.get(
                "approval_status"
            )
        )

        # --------------------------------------------------
        # Human approval required
        # --------------------------------------------------

        if result.get(
            "requires_approval"
        ):

            print(
                "\nHuman approval is required "
                "before continuing."
            )

            decision = input(
                "Approve action? "
                "(approve/reject): "
            ).strip().lower()

            if decision not in {
                "approve",
                "reject",
            }:
                print(
                    "\nInvalid response. "
                    "Defaulting to reject."
                )

                decision = "reject"

            resumed_result = resume_agent(
                decision,
                thread_id,
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

        # --------------------------------------------------
        # No approval required
        # --------------------------------------------------

        else:

            print(
                "\nNo human approval required."
            )

            print(
                "\nACTION RESULT"
            )

            print(
                result.get(
                    "action_result"
                )
            )
