import json
import os
from functools import lru_cache
from typing import Dict, List, Any

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

KNOWLEDGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "operations_knowledge.json",
)

EMBEDDING_MODEL = "text-embedding-3-small"

_client = None


def get_client() -> OpenAI:
    """Create the OpenAI client only when it is needed."""
    global _client

    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    return _client


def load_knowledge() -> List[Dict[str, Any]]:
    """Load operations knowledge entries from JSON."""
    with open(
        KNOWLEDGE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def knowledge_to_text(
    item: Dict[str, Any]
) -> str:
    """
    Convert a knowledge record into text suitable
    for embedding.
    """
    topic = str(
        item.get("topic", "")
    ).strip()

    content = str(
        item.get("content", "")
    ).strip()

    return f"Topic: {topic}\nContent: {content}"


def create_embedding(
    text: str
) -> np.ndarray:
    """Generate an embedding using OpenAI."""
    response = get_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return np.array(
        response.data[0].embedding,
        dtype=np.float32,
    )


def cosine_similarity(
    vector_a: np.ndarray,
    vector_b: np.ndarray,
) -> float:
    """Calculate cosine similarity between two vectors."""
    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b)
        / denominator
    )


@lru_cache(maxsize=1)
def build_knowledge_index():
    """
    Embed the small local knowledge base once per process.

    For a production-scale corpus this would normally
    be stored in a vector database instead.
    """
    knowledge = load_knowledge()

    texts = [
        knowledge_to_text(item)
        for item in knowledge
    ]

    if not texts:
        return []

    response = get_client().embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    index = []

    for item, embedding_data in zip(
        knowledge,
        response.data,
    ):
        index.append(
            {
                "item": item,
                "embedding": np.array(
                    embedding_data.embedding,
                    dtype=np.float32,
                ),
            }
        )

    return index


def search_knowledge(
    query: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Retrieve semantically relevant knowledge entries.

    Results are ordered by embedding cosine similarity.
    """
    if not query.strip():
        return []

    index = build_knowledge_index()

    if not index:
        return []

    query_embedding = create_embedding(
        query
    )

    scored_results = []

    for record in index:
        score = cosine_similarity(
            query_embedding,
            record["embedding"],
        )

        result = dict(
            record["item"]
        )

        result["similarity_score"] = round(
            score,
            4,
        )

        scored_results.append(
            result
        )

    scored_results.sort(
        key=lambda item: item[
            "similarity_score"
        ],
        reverse=True,
    )

    return scored_results[:top_k]


if __name__ == "__main__":
    results = search_knowledge(
        "How should we respond to a severe production outage?"
    )

    print(
        "\nSEMANTIC KNOWLEDGE RESULTS"
    )

    for result in results:
        print(
            "\nTopic:",
            result.get("topic"),
        )
        print(
            "Similarity:",
            result.get("similarity_score"),
        )
        print(
            "Content:",
            result.get("content"),
        )
