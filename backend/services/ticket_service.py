from datetime import datetime, timezone
from random import randint

from database.mongodb import ticket_collection


def generate_ticket_id() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_part = randint(1000, 9999)

    return f"TN-{date_part}-{random_part}"


def create_ticket(
    email: str,
    product: str,
    issue: str,
    priority: str = "Medium"
) -> dict:
    ticket = {
        "ticket_id": generate_ticket_id(),
        "email": email,
        "product": product,
        "issue": issue,
        "priority": priority,
        "status": "Open",
        "created_at": datetime.now(timezone.utc)
    }

    ticket_collection.insert_one(ticket)

    ticket.pop("_id", None)

    return ticket


def get_user_tickets(email: str) -> list[dict]:
    tickets = list(
        ticket_collection.find(
            {"email": email},
            {"_id": 0}
        ).sort("created_at", -1)
    )

    return tickets


def update_ticket_status(
    ticket_id: str,
    status: str
) -> bool:
    result = ticket_collection.update_one(
        {"ticket_id": ticket_id},
        {"$set": {"status": status}}
    )

    return result.modified_count > 0
