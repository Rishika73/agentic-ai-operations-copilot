import json
from pathlib import Path
from typing import Dict, List


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "operations_knowledge.json"
)


def load_knowledge() -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_knowledge(query: str) -> List[Dict]:
    query_terms = set(query.lower().split())

    results = []

    for item in load_knowledge():
        searchable_text = (
            item["topic"] + " " + item["content"]
        ).lower()

        score = sum(
            1
            for term in query_terms
            if term in searchable_text
        )

        if score > 0:
            result = item.copy()
            result["score"] = score
            results.append(result)

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return results
