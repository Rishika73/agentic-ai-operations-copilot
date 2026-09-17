import numpy as np

import tools.knowledge_tool as knowledge_tool


def fake_embedding_for_text(text: str) -> np.ndarray:
    text = text.lower()

    if "severe production outage" in text:
        return np.array([1.0, 0.0, 0.0], dtype=np.float32)

    if "critical incident response" in text:
        return np.array([0.95, 0.05, 0.0], dtype=np.float32)

    if "high priority incident response" in text:
        return np.array([0.8, 0.2, 0.0], dtype=np.float32)

    if "customer health" in text:
        return np.array([0.2, 0.8, 0.0], dtype=np.float32)

    if "renewal risk" in text:
        return np.array([0.1, 0.9, 0.0], dtype=np.float32)

    if "customer retention risk" in text:
        return np.array([0.1, 0.95, 0.0], dtype=np.float32)

    if "incident response" in text:
        return np.array([0.9, 0.1, 0.0], dtype=np.float32)

    return np.array([0.0, 0.0, 1.0], dtype=np.float32)


def build_fake_index():
    knowledge = knowledge_tool.load_knowledge()

    return [
        {
            "item": item,
            "embedding": fake_embedding_for_text(
                knowledge_tool.knowledge_to_text(item)
            ),
        }
        for item in knowledge
    ]


def test_semantic_search_returns_critical_incident_first(monkeypatch):
    monkeypatch.setattr(
        knowledge_tool,
        "build_knowledge_index",
        build_fake_index,
    )

    monkeypatch.setattr(
        knowledge_tool,
        "create_embedding",
        fake_embedding_for_text,
    )

    results = knowledge_tool.search_knowledge(
        "How should we respond to a severe production outage?",
        top_k=3,
    )

    assert results
    assert results[0]["topic"] == "critical incident response"


def test_semantic_search_returns_similarity_scores(monkeypatch):
    monkeypatch.setattr(
        knowledge_tool,
        "build_knowledge_index",
        build_fake_index,
    )

    monkeypatch.setattr(
        knowledge_tool,
        "create_embedding",
        fake_embedding_for_text,
    )

    results = knowledge_tool.search_knowledge(
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


def test_semantic_search_respects_top_k(monkeypatch):
    monkeypatch.setattr(
        knowledge_tool,
        "build_knowledge_index",
        build_fake_index,
    )

    monkeypatch.setattr(
        knowledge_tool,
        "create_embedding",
        fake_embedding_for_text,
    )

    results = knowledge_tool.search_knowledge(
        "incident response",
        top_k=2,
    )

    assert len(results) == 2
