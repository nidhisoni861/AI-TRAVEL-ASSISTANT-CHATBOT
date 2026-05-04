"""Endpoints for chat history, user preferences, and mock bookings.

Routes:
  GET  /chat-history/{session_id}  — load conversation history
  POST /save-preferences           — save/update travel preferences
  GET  /preferences/{session_id}   — read stored preferences
  POST /mock-booking               — record a simulated booking
  GET  /bookings/{session_id}      — list bookings for a session
"""

from __future__ import annotations

import sys
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Allow importing database.py from backend/
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from database import get_db, User, TravelPreference, ChatMessage, MockBooking

router = APIRouter(prefix="", tags=["history"])


# ── Pydantic request / response schemas ────────────────────────────────────

class PreferencesRequest(BaseModel):
    session_id: str
    budget:       Optional[str] = None
    pace:         Optional[str] = None
    travel_style: Optional[str] = None
    interests:    list[str] = []
    dietary:      list[str] = []
    home_city:    Optional[str] = None
    currency:     Optional[str] = "EUR"


class PreferencesResponse(BaseModel):
    session_id: str
    budget:       Optional[str]
    pace:         Optional[str]
    travel_style: Optional[str]
    interests:    list[str]
    dietary:      list[str]
    home_city:    Optional[str]
    currency:     Optional[str]


class ChatHistoryMessage(BaseModel):
    role:      str
    content:   str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages:   list[ChatHistoryMessage]


class MockBookingRequest(BaseModel):
    session_id:      str
    booking_type:    str          # "flight" | "hotel"
    item_id:         str
    passenger_name:  str
    email:           str
    summary:         Optional[str] = None


class MockBookingResponse(BaseModel):
    booking_reference: str
    status:            str
    booking_type:      str
    summary:           str
    is_mock:           bool = True


# ── Helpers ────────────────────────────────────────────────────────────────

def _get_or_create_user(session_id: str, db: Session) -> User:
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        user = User(session_id=session_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


import uuid

def _generate_booking_ref() -> str:
    return "BK-" + str(uuid.uuid4()).upper()[:8]


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/chat-history/{session_id}", response_model=ChatHistoryResponse)
def get_chat_history(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Return the last `limit` messages for a session."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        return ChatHistoryResponse(session_id=session_id, messages=[])

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[
            ChatHistoryMessage(
                role=m.role,
                content=m.content,
                timestamp=m.timestamp.isoformat(),
            )
            for m in messages
        ],
    )


@router.post("/save-preferences", response_model=PreferencesResponse)
def save_preferences(req: PreferencesRequest, db: Session = Depends(get_db)):
    """Create or update travel preferences for a session."""
    user = _get_or_create_user(req.session_id, db)

    prefs = db.query(TravelPreference).filter(TravelPreference.user_id == user.id).first()
    if prefs:
        prefs.budget       = req.budget
        prefs.pace         = req.pace
        prefs.travel_style = req.travel_style
        prefs.interests    = req.interests
        prefs.dietary      = req.dietary
        prefs.home_city    = req.home_city
        prefs.currency     = req.currency
    else:
        prefs = TravelPreference(
            user_id      = user.id,
            budget       = req.budget,
            pace         = req.pace,
            travel_style = req.travel_style,
            interests    = req.interests,
            dietary      = req.dietary,
            home_city    = req.home_city,
            currency     = req.currency,
        )
        db.add(prefs)

    db.commit()
    db.refresh(prefs)

    return PreferencesResponse(
        session_id   = req.session_id,
        budget       = prefs.budget,
        pace         = prefs.pace,
        travel_style = prefs.travel_style,
        interests    = prefs.interests or [],
        dietary      = prefs.dietary or [],
        home_city    = prefs.home_city,
        currency     = prefs.currency,
    )


@router.get("/preferences/{session_id}", response_model=PreferencesResponse)
def get_preferences(session_id: str, db: Session = Depends(get_db)):
    """Load stored travel preferences for a session."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user or not user.preferences:
        return PreferencesResponse(
            session_id=session_id,
            budget=None, pace=None, travel_style=None,
            interests=[], dietary=[], home_city=None, currency="EUR",
        )
    p = user.preferences
    return PreferencesResponse(
        session_id   = session_id,
        budget       = p.budget,
        pace         = p.pace,
        travel_style = p.travel_style,
        interests    = p.interests or [],
        dietary      = p.dietary or [],
        home_city    = p.home_city,
        currency     = p.currency,
    )


@router.post("/mock-booking", response_model=MockBookingResponse)
def create_mock_booking(req: MockBookingRequest, db: Session = Depends(get_db)):
    """Simulate a booking and persist it."""
    user = _get_or_create_user(req.session_id, db)

    ref = _generate_booking_ref()
    summary = req.summary or f"Mock {req.booking_type} booking for {req.passenger_name} (item {req.item_id})"

    booking = MockBooking(
        user_id           = user.id,
        booking_reference = ref,
        booking_type      = req.booking_type,
        item_id           = req.item_id,
        passenger_name    = req.passenger_name,
        email             = req.email,
        summary           = summary,
        status            = "confirmed",
        is_mock           = True,
    )
    db.add(booking)
    db.commit()

    return MockBookingResponse(
        booking_reference = ref,
        status            = "confirmed",
        booking_type      = req.booking_type,
        summary           = summary,
        is_mock           = True,
    )


@router.get("/bookings/{session_id}")
def get_bookings(session_id: str, db: Session = Depends(get_db)):
    """Return all mock bookings for a session."""
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        return {"session_id": session_id, "bookings": []}

    bookings = db.query(MockBooking).filter(MockBooking.user_id == user.id).all()
    return {
        "session_id": session_id,
        "bookings": [
            {
                "booking_reference": b.booking_reference,
                "type":              b.booking_type,
                "summary":           b.summary,
                "status":            b.status,
                "created_at":        b.created_at.isoformat(),
            }
            for b in bookings
        ],
    }
