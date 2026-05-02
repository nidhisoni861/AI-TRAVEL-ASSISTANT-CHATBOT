"""Amadeus Self-Service flight search.

Falls back to mock data if AMADEUS_API_KEY is not configured.
"""
from __future__ import annotations

import time
from typing import Optional

import httpx
from loguru import logger

from app.config import get_settings
from app.models.schemas import FlightSearchRequest, FlightSearchResponse, FlightOffer


_token_cache: dict = {"access_token": None, "expires_at": 0.0}


async def _get_token() -> Optional[str]:
    s = get_settings()
    if not (s.amadeus_api_key and s.amadeus_api_secret):
        return None
    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now + 30:
        return _token_cache["access_token"]
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": s.amadeus_api_key,
                    "client_secret": s.amadeus_api_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            data = resp.json()
            _token_cache["access_token"] = data["access_token"]
            _token_cache["expires_at"] = now + data.get("expires_in", 1800)
            return _token_cache["access_token"]
    except Exception as e:
        logger.exception(f"Amadeus token fetch failed: {e}")
        return None


def _mock(req: FlightSearchRequest) -> FlightSearchResponse:
    base = 220 + (hash((req.origin, req.destination)) % 200)
    offers = [
        FlightOffer(
            id=f"MOCK-{i}",
            airline=airline,
            departure=f"{req.departure_date}T{8 + i*3:02d}:00",
            arrival=f"{req.departure_date}T{12 + i*3:02d}:30",
            duration="PT4H30M",
            stops=stops,
            price_total=round(base + i * 35, 2),
            currency="EUR",
            booking_link=None,
        )
        for i, (airline, stops) in enumerate([
            ("Lufthansa", 0),
            ("Air France", 1),
            ("Ryanair", 0),
            ("KLM", 1),
        ])
    ]
    return FlightSearchResponse(offers=offers, is_mock=True)


async def search_flights(req: FlightSearchRequest) -> FlightSearchResponse:
    token = await _get_token()
    if token is None:
        logger.info("Amadeus credentials missing; returning mock flights")
        return _mock(req)

    params = {
        "originLocationCode": req.origin,
        "destinationLocationCode": req.destination,
        "departureDate": req.departure_date.isoformat(),
        "adults": req.adults,
        "travelClass": req.travel_class,
        "max": 10,
        "currencyCode": "EUR",
    }
    if req.return_date:
        params["returnDate"] = req.return_date.isoformat()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                "https://test.api.amadeus.com/v2/shopping/flight-offers",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception(f"Amadeus flight search failed, falling back to mock: {e}")
        return _mock(req)

    offers: list[FlightOffer] = []
    for raw in data.get("data", [])[:10]:
        try:
            it = raw["itineraries"][0]
            seg_first = it["segments"][0]
            seg_last = it["segments"][-1]
            offers.append(FlightOffer(
                id=raw["id"],
                airline=seg_first["carrierCode"],
                departure=seg_first["departure"]["at"],
                arrival=seg_last["arrival"]["at"],
                duration=it["duration"],
                stops=max(0, len(it["segments"]) - 1),
                price_total=float(raw["price"]["total"]),
                currency=raw["price"]["currency"],
            ))
        except Exception as e:
            logger.warning(f"Skipping malformed Amadeus offer: {e}")
    return FlightSearchResponse(offers=offers, is_mock=False)
