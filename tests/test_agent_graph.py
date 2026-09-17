from app.agent_graph import router_node


def test_routes_incident_query():
    state = {
        "user_query": "What open incidents do we have?"
    }

    result = router_node(state)

    assert result["route"] == "incident"


def test_routes_account_risk_query():
    state = {
        "user_query": "Which customer accounts are at risk?"
    }

    result = router_node(state)

    assert result["route"] == "account_risk"


def test_routes_policy_query_to_knowledge():
    state = {
        "user_query": "What is the policy for critical incident response?"
    }

    result = router_node(state)

    assert result["route"] == "knowledge"


def test_defaults_to_knowledge():
    state = {
        "user_query": "Explain our operational guidance."
    }

    result = router_node(state)

    assert result["route"] == "knowledge"
