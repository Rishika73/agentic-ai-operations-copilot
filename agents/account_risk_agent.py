from typing import Dict, Any

from app.llm import generate_operational_answer
from tools.crm_tool import (
    get_at_risk_accounts,
    get_accounts_renewing_within,
)


def run_account_risk_agent(user_query: str) -> Dict[str, Any]:
    accounts = get_at_risk_accounts()
    renewals = get_accounts_renewing_within(30)

    tool_results = [
        {
            "tool": "crm",
            "at_risk_accounts": accounts,
            "renewing_within_30_days": renewals,
        }
    ]

    answer = generate_operational_answer(
        user_query=user_query,
        route="account_risk",
        tool_results=tool_results,
        retrieved_context=[],
    )

    return {
        "agent": "account_risk_agent",
        "tool_results": tool_results,
        "answer": answer,
    }


if __name__ == "__main__":
    result = run_account_risk_agent(
        "Which customer accounts are at risk?"
    )

    print("\nAGENT")
    print(result["agent"])

    print("\nANSWER")
    print(result["answer"])
