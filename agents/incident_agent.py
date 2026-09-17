from typing import Dict, Any

from app.llm import generate_operational_answer
from tools.ticket_tool import get_open_incidents


def run_incident_agent(user_query: str) -> Dict[str, Any]:
    incidents = get_open_incidents()

    tool_results = [
        {
            "tool": "support_tickets",
            "open_incidents": incidents,
        }
    ]

    answer = generate_operational_answer(
        user_query=user_query,
        route="incident",
        tool_results=tool_results,
        retrieved_context=[],
    )

    return {
        "agent": "incident_agent",
        "tool_results": tool_results,
        "answer": answer,
    }


if __name__ == "__main__":
    result = run_incident_agent(
        "What open incidents do we have?"
    )

    print("\nAGENT")
    print(result["agent"])

    print("\nANSWER")
    print(result["answer"])
