from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from auth.jwt_handler import verify_access_token
from services.ticket_service import (
    create_ticket,
    get_user_tickets,
    update_ticket_status
)


router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


class TicketRequest(BaseModel):
    product: str
    issue: str
    priority: str = "Medium"


class TicketStatusRequest(BaseModel):
    status: str


def get_email_from_token(authorization: str) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format."
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    email = verify_access_token(token)

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    return email


@router.post("")
def create_new_ticket(
    request: TicketRequest,
    authorization: str = Header(None)
):
    email = get_email_from_token(authorization)

    ticket = create_ticket(
        email=email,
        product=request.product,
        issue=request.issue,
        priority=request.priority
    )

    return {
        "message": "Ticket created successfully.",
        "ticket": ticket
    }


@router.get("")
def list_tickets(
    authorization: str = Header(None)
):
    email = get_email_from_token(authorization)

    return {
        "tickets": get_user_tickets(email)
    }


@router.patch("/{ticket_id}")
def change_ticket_status(
    ticket_id: str,
    request: TicketStatusRequest,
    authorization: str = Header(None)
):
    get_email_from_token(authorization)

    updated = update_ticket_status(
        ticket_id=ticket_id,
        status=request.status
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found or status unchanged."
        )

    return {
        "message": "Ticket status updated."
    }
