"""Simulated booking — generates a fake confirmation reference.

Real payment integration is intentionally out of scope for an academic project.
"""
import random
import string

from app.models.schemas import BookingRequest, BookingResponse


def _ref() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def simulate_booking(req: BookingRequest) -> BookingResponse:
    return BookingResponse(
        booking_reference=f"WND-{_ref()}",
        status="confirmed",
        type=req.type,
        summary=(
            f"Confirmed {req.type} booking for {req.passenger_name} "
            f"(item {req.item_id}). Confirmation sent to {req.email}."
        ),
        is_mock=True,
    )
