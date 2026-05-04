"""SQLAlchemy database models and session management.

Tables:
  - users             : registered user accounts
  - travel_preferences: per-user travel preferences
  - chat_messages     : full conversation history (per session)
  - itineraries       : saved itinerary plans
  - mock_bookings     : simulated flight/hotel bookings

Usage:
    from database import SessionLocal, init_db
    init_db()                     # call once at startup
    db = SessionLocal()           # get a session
    db.close()                    # always close it
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# ── Engine ──────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "travel_assistant.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite + FastAPI
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Helper ──────────────────────────────────────────────────────────────────
def _new_id() -> str:
    return str(uuid.uuid4())


# ── Models ──────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=_new_id)
    session_id = Column(String, unique=True, nullable=False, index=True)
    name       = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    preferences = relationship("TravelPreference", back_populates="user", uselist=False, cascade="all, delete")
    messages    = relationship("ChatMessage",      back_populates="user", cascade="all, delete")
    bookings    = relationship("MockBooking",       back_populates="user", cascade="all, delete")
    itineraries = relationship("Itinerary",         back_populates="user", cascade="all, delete")


class TravelPreference(Base):
    __tablename__ = "travel_preferences"

    id          = Column(String, primary_key=True, default=_new_id)
    user_id     = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    budget      = Column(String, nullable=True)       # "budget" | "mid-range" | "luxury"
    pace        = Column(String, nullable=True)       # "relaxed" | "balanced" | "packed"
    travel_style = Column(String, nullable=True)      # "solo" | "couple" | "family" | "group"
    interests   = Column(JSON,   nullable=True)       # list of strings
    dietary     = Column(JSON,   nullable=True)       # list of strings
    home_city   = Column(String, nullable=True)
    currency    = Column(String, nullable=True, default="EUR")
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(String,  primary_key=True, default=_new_id)
    user_id    = Column(String,  ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String,  nullable=False, index=True)
    role       = Column(String,  nullable=False)     # "user" | "assistant"
    content    = Column(Text,    nullable=False)
    tool_calls = Column(JSON,    nullable=True)       # serialised ToolCall list
    citations  = Column(JSON,    nullable=True)       # list of source strings
    timestamp  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id          = Column(String,  primary_key=True, default=_new_id)
    user_id     = Column(String,  ForeignKey("users.id"), nullable=False)
    destination = Column(String,  nullable=False)
    days        = Column(Integer, nullable=False)
    summary     = Column(Text,    nullable=True)
    data        = Column(JSON,    nullable=False)     # full ItineraryResponse as dict
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="itineraries")


class MockBooking(Base):
    __tablename__ = "mock_bookings"

    id                 = Column(String,  primary_key=True, default=_new_id)
    user_id            = Column(String,  ForeignKey("users.id"), nullable=False)
    booking_reference  = Column(String,  unique=True, nullable=False)
    booking_type       = Column(String,  nullable=False)   # "flight" | "hotel"
    item_id            = Column(String,  nullable=False)
    passenger_name     = Column(String,  nullable=False)
    email              = Column(String,  nullable=False)
    summary            = Column(Text,    nullable=True)
    status             = Column(String,  default="confirmed")
    is_mock            = Column(Boolean, default=True)
    created_at         = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")


# ── Init ────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables (idempotent — safe to call on every startup)."""
    Base.metadata.create_all(bind=engine)


# ── FastAPI dependency ───────────────────────────────────────────────────────

def get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
