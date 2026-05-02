"""Lightweight rule-based tool router.

A small fine-tuned model (Gemma 2B) is *not* reliably good at JSON tool-calling.
Instead of forcing a fragile function-calling format on it, we do a deterministic
intent classifier here, dispatch the tool, then pass the result back to the LLM
as additional context for the final reply. This pattern is simpler, more
demoable, and works whether or not the user has fine-tuned the model.
"""
import re
from datetime import date, timedelta
from typing import Optional

from app.models.schemas import (
    FlightSearchRequest,
    WeatherRequest,
    PlacesRequest,
    ToolCall,
)
from app.services import amadeus_service, weather_service, places_service


# very small heuristic — good enough for a demo
IATA_RE = re.compile(r"\b([A-Z]{3})\b")
WEATHER_KEYWORDS = ("weather", "forecast", "temperature", "rain", "sunny", "climate")
FLIGHT_KEYWORDS = ("flight", "fly", "airfare", "ticket", "from .* to ", "airport")
PLACE_KEYWORDS = (
    "attraction", "things to do", "what to see", "restaurant", "food",
    "where to eat", "hotel", "stay", "visit", "museum",
)
ITINERARY_KEYWORDS = ("itinerary", "plan a", "trip plan", "day-by-day", "days in")


def _extract_city(text: str) -> Optional[str]:
    # naive: "weather in Paris", "in Tokyo", "to Rome"
    m = re.search(r"(?:in|to|for|at|near)\s+([A-Z][a-zA-Z\- ]{2,30}?)(?:[\?\.\,]|$|\s+(?:on|tomorrow|today|next))", text)
    if m:
        return m.group(1).strip()
    return None


def _extract_iata(text: str) -> Optional[str]:
    m = IATA_RE.search(text)
    return m.group(1) if m else None


def detect_intent(text: str) -> Optional[str]:
    lower = text.lower()
    if any(k in lower for k in WEATHER_KEYWORDS):
        return "weather"
    if any(k in lower for k in FLIGHT_KEYWORDS):
        return "flights"
    if any(k in lower for k in ITINERARY_KEYWORDS):
        return "itinerary"
    if any(k in lower for k in PLACE_KEYWORDS):
        return "places"
    return None


async def maybe_run_tool(text: str) -> Optional[ToolCall]:
    intent = detect_intent(text)
    if intent is None:
        return None

    if intent == "weather":
        city = _extract_city(text)
        if not city:
            return None
        result = await weather_service.get_weather(WeatherRequest(city=city))
        return ToolCall(tool="weather", args={"city": city}, result=result.model_dump())

    if intent == "flights":
        # very rough parse: "flights from FRA to CDG"
        m = re.search(r"from\s+([A-Z]{3}).*?to\s+([A-Z]{3})", text)
        if not m:
            m = re.search(r"from\s+([A-Z][a-zA-Z]+).*?to\s+([A-Z][a-zA-Z]+)", text)
        if not m:
            return None
        origin, dest = m.group(1), m.group(2)
        # If we got city names, we'd need a city→IATA lookup. For demo, accept either.
        if len(origin) != 3 or len(dest) != 3:
            return None
        dep = date.today() + timedelta(days=14)
        result = await amadeus_service.search_flights(
            FlightSearchRequest(origin=origin, destination=dest, departure_date=dep)
        )
        return ToolCall(
            tool="flight_search",
            args={"origin": origin, "destination": dest, "departure_date": str(dep)},
            result=result.model_dump(),
        )

    if intent == "places":
        city = _extract_city(text) or _extract_iata(text)
        if not city:
            return None
        category = "restaurants" if "restaurant" in text.lower() or "eat" in text.lower() else "attractions"
        result = await places_service.get_places(
            PlacesRequest(location=city, category=category, limit=6)
        )
        return ToolCall(
            tool="places",
            args={"location": city, "category": category},
            result=result.model_dump(),
        )

    return None


def format_tool_result_for_llm(tc: ToolCall) -> str:
    """Render a tool result into a short text block the LLM can read as context."""
    if tc.tool == "weather":
        r = tc.result
        return (
            f"[WEATHER] {r['city']}: {r['temp_c']:.0f}°C, {r['description']}, "
            f"humidity {r['humidity']}%."
        )
    if tc.tool == "flight_search":
        offers = tc.result.get("offers", [])[:5]
        lines = [f"[FLIGHTS] {tc.args['origin']}→{tc.args['destination']} on {tc.args['departure_date']}:"]
        for o in offers:
            lines.append(
                f"- {o['airline']} {o['departure']}→{o['arrival']} "
                f"({o['duration']}, {o['stops']} stops) {o['currency']}{o['price_total']}"
            )
        return "\n".join(lines)
    if tc.tool == "places":
        places = tc.result.get("places", [])[:6]
        lines = [f"[{tc.args['category'].upper()} in {tc.args['location']}]:"]
        for p in places:
            rating = f" ★{p['rating']}" if p.get("rating") else ""
            lines.append(f"- {p['name']}{rating} — {p.get('description') or p.get('address') or ''}")
        return "\n".join(lines)
    return ""
