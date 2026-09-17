from tools.knowledge_tool import search_knowledge


def test_semantic_search_returns_critical_incident_first():
    results = search_knowledge(
        "How should we respond to a severe production outage?",
        top_k=3,
    )

    assert results
    assert results[0]["topic"] == "critical incident response"


def test_semantic_search_returns_similarity_scores():
    results = search_knowledge(
        "customer retention risk",
        top_k=3,
    )

    assert results

    for result in results:
        assert "similarity_score" in result
        assert isinstance(
            result["similarity_score"],
            float,
        )


def test_semantic_search_respects_top_k():
    results = search_knowledge(
        "incident response",
        top_k=2,
    )

    assert len(results) == 2
