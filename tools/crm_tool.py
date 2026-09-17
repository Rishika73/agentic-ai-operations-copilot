import json
from pathlib import Path
from typing import Dict, List, Optional


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "customer_accounts.json"
)


def load_accounts() -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_customer_account(
    customer: str
) -> Optional[Dict]:
    for account in load_accounts():
        if account["customer"].lower() == customer.lower():
            return account

    return None


def get_at_risk_accounts() -> List[Dict]:
    return [
        account
        for account in load_accounts()
        if account["risk_level"].lower() == "high"
    ]


def get_accounts_renewing_within(
    days: int
) -> List[Dict]:
    return [
        account
        for account in load_accounts()
        if account["renewal_days"] <= days
    ]
