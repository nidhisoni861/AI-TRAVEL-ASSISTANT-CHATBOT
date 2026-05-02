"""OpenWeatherMap current weather. Falls back to mock if API key missing."""
import httpx
from loguru import logger

from app.config import get_settings
from app.models.schemas import WeatherRequest, WeatherResponse


def _mock(req: WeatherRequest) -> WeatherResponse:
    seed = sum(ord(c) for c in req.city) % 30
    return WeatherResponse(
        city=req.city,
        country=req.country or "??",
        temp_c=18.0 + seed % 10,
        feels_like_c=17.0 + seed % 10,
        humidity=55 + seed % 20,
        description="partly cloudy",
        icon="02d",
        is_mock=True,
    )


async def get_weather(req: WeatherRequest) -> WeatherResponse:
    s = get_settings()
    if not s.openweathermap_api_key:
        return _mock(req)

    q = f"{req.city},{req.country}" if req.country else req.city
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": q, "appid": s.openweathermap_api_key, "units": "metric"}

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception(f"OWM call failed, falling back: {e}")
        return _mock(req)

    return WeatherResponse(
        city=data.get("name", req.city),
        country=data.get("sys", {}).get("country", req.country or "??"),
        temp_c=data["main"]["temp"],
        feels_like_c=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        description=data["weather"][0]["description"],
        icon=data["weather"][0]["icon"],
        is_mock=False,
    )
