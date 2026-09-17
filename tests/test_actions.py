from app.actions import propose_action, execute_action


def test_incident_proposes_escalation():
    state = {
        "route": "incident",
        "user_query": "What open incidents do we have?",
    }

    result = propose_action(state)

    assert result["requires_approval"] is True
    assert result["approval_status"] == "pending"
    assert result["proposed_action"]["action_type"] == "incident_escalation"


def test_account_risk_proposes_customer_outreach():
    state = {
        "route": "account_risk",
        "user_query": "Which accounts are at risk?",
    }

    result = propose_action(state)

    assert result["requires_approval"] is True
    assert result["approval_status"] == "pending"
    assert result["proposed_action"]["action_type"] == "customer_outreach"


def test_knowledge_requires_no_action():
    state = {
        "route": "knowledge",
        "user_query": "What is the incident response policy?",
    }

    result = propose_action(state)

    assert result["requires_approval"] is False
    assert result["approval_status"] == "not_required"
    assert result["proposed_action"]["action_type"] == "no_action"


def test_analysis_only_prevents_action():
    state = {
        "route": "incident",
        "user_query": "Show open incidents, analysis only",
    }

    result = propose_action(state)

    assert result["requires_approval"] is False
    assert result["proposed_action"]["action_type"] == "no_action"


def test_rejected_action_not_executed():
    state = {
        "approval_status": "rejected",
        "proposed_action": {
            "action_type": "incident_escalation",
        },
    }

    result = execute_action(state)

    assert result["action_result"]["status"] == "not_executed"


def test_approved_incident_action_executes():
    state = {
        "approval_status": "approved",
        "proposed_action": {
            "action_type": "incident_escalation",
        },
    }

    result = execute_action(state)

    assert result["action_result"]["status"] == "executed"
    assert (
        result["action_result"]["action_type"]
        == "incident_escalation"
    )


def test_no_action_executes_safely():
    state = {
        "approval_status": "not_required",
        "proposed_action": {
            "action_type": "no_action",
        },
    }

    result = execute_action(state)

    assert result["action_result"]["status"] == "no_action"
