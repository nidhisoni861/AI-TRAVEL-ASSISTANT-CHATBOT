from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ---------- Chat ----------

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class UserPreferences(BaseModel):
    budget: Optional[Literal["budget", "mid-range", "luxury"]] = None
    interests: list[str] = Field(default_factory=list, description="e.g. food, history, adventure")
    pace: Optional[Literal["relaxed", "balanced", "packed"]] = None
    travel_style: Optional[Literal["solo", "couple", "family", "group"]] = None
    dietary: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Stable id for multi-turn memory")
    message: str
    preferences: Optional[UserPreferences] = None


class ToolCall(BaseModel):
    tool: str
    args: dict
    result: dict | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


# ---------- Flights ----------

class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="IATA code, e.g. FRA")
    destination: str = Field(..., description="IATA code, e.g. CDG")
    departure_date: date
    return_date: Optional[date] = None
    adults: int = 1
    travel_class: Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"] = "ECONOMY"


class FlightOffer(BaseModel):
    id: str
    airline: str
    departure: str
    arrival: str
    duration: str
    stops: int
    price_total: float
    currency: str
    booking_link: Optional[str] = None


class FlightSearchResponse(BaseModel):
    offers: list[FlightOffer]
    is_mock: bool = False


# ---------- Weather ----------

class WeatherRequest(BaseModel):
    city: str
    country: Optional[str] = None


class WeatherResponse(BaseModel):
    city: str
    country: str
    temp_c: float
    feels_like_c: float
    humidity: int
    description: str
    icon: str
    is_mock: bool = False


# ---------- Places ----------

class PlacesRequest(BaseModel):
    location: str
    category: Literal["attractions", "restaurants", "hotels", "events"] = "attractions"
    limit: int = 10


class Place(BaseModel):
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class PlacesResponse(BaseModel):
    location: str
    places: list[Place]
    is_mock: bool = False


# ---------- Itinerary ----------

class ItineraryRequest(BaseModel):
    destination: str
    days: int = Field(..., ge=1, le=14)
    start_date: Optional[date] = None
    preferences: Optional[UserPreferences] = None


class ItineraryActivity(BaseModel):
    time: str  # "Morning", "Afternoon", "Evening" or "09:00"
    title: str
    description: str
    estimated_cost: Optional[str] = None


class ItineraryDay(BaseModel):
    day: int
    date: Optional[date] = None
    title: str
    activities: list[ItineraryActivity]


class ItineraryResponse(BaseModel):
    destination: str
    days: int
    summary: str
    itinerary: list[ItineraryDay]


# ---------- Booking simulation ----------

class BookingRequest(BaseModel):
    type: Literal["flight", "hotel"]
    item_id: str
    passenger_name: str
    email: str


class BookingResponse(BaseModel):
    booking_reference: str
    status: Literal["confirmed", "pending"] = "confirmed"
    type: str
    summary: str
    is_mock: bool = True
