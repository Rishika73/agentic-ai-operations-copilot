from typing import Dict, Any

from app.llm import generate_operational_answer
from tools.knowledge_tool import search_knowledge


def run_knowledge_agent(user_query: str) -> Dict[str, Any]:
    retrieved_context = search_knowledge(user_query)

    answer = generate_operational_answer(
        user_query=user_query,
        route="knowledge",
        tool_results=[],
        retrieved_context=retrieved_context,
    )

    return {
        "agent": "knowledge_agent",
        "retrieved_context": retrieved_context,
        "answer": answer,
    }


if __name__ == "__main__":
    result = run_knowledge_agent(
        "What is the policy for critical incident response?"
    )

    print("\nAGENT")
    print(result["agent"])

    print("\nANSWER")
    print(result["answer"])
