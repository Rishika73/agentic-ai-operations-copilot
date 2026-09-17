import json
from pathlib import Path
from typing import Dict, List, Optional


DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "support_tickets.json"
)


def load_tickets() -> List[Dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_tickets(
    customer: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Dict]:
    tickets = load_tickets()

    results = []

    for ticket in tickets:
        if (
            customer
            and ticket["customer"].lower() != customer.lower()
        ):
            continue

        if (
            priority
            and ticket["priority"].lower() != priority.lower()
        ):
            continue

        if (
            status
            and ticket["status"].lower() != status.lower()
        ):
            continue

        results.append(ticket)

    return results


def get_open_incidents() -> List[Dict]:
    return [
        ticket
        for ticket in load_tickets()
        if ticket.get("status", "").lower() == "open"
    ]
