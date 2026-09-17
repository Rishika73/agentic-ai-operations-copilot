from typing import Dict, Any

from langgraph.types import interrupt

from app.state import AgentState


def propose_action(state: AgentState) -> Dict[str, Any]:
    route = state.get("route")
    query = state.get("user_query", "").lower()

    if route == "account_risk":
        proposed_action = {
            "action_type": "customer_outreach",
            "description": (
                "Prepare a proactive customer-success outreach plan "
                "for the highest-risk account."
            ),
        }
        requires_approval = True

    elif route == "incident":
        proposed_action = {
            "action_type": "incident_escalation",
            "description": (
                "Prepare an escalation request for the highest-priority "
                "open incident."
            ),
        }
        requires_approval = True

    else:
        proposed_action = {
            "action_type": "no_action",
            "description": (
                "No operational action is required for this knowledge request."
            ),
        }
        requires_approval = False

    if (
        "do not take action" in query
        or "analysis only" in query
    ):
        proposed_action = {
            "action_type": "no_action",
            "description": "User requested analysis only.",
        }
        requires_approval = False

    return {
        "proposed_action": proposed_action,
        "requires_approval": requires_approval,
        "approval_status": (
            "pending"
            if requires_approval
            else "not_required"
        ),
    }


def human_approval_node(state: AgentState) -> Dict[str, Any]:
    if not state.get("requires_approval", False):
        return {
            "approval_status": "not_required"
        }

    decision = interrupt(
        {
            "message": "Human approval required",
            "proposed_action": state.get("proposed_action"),
        }
    )

    approved = str(decision).lower() in {
        "approve",
        "approved",
        "yes",
        "y",
        "true",
    }

    return {
        "approval_status": (
            "approved"
            if approved
            else "rejected"
        )
    }
