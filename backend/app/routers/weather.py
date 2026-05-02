from fastapi import APIRouter
from app.models.schemas import WeatherRequest, WeatherResponse
from app.services import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])


@router.post("", response_model=WeatherResponse)
async def get_weather(req: WeatherRequest):
    return await weather_service.get_weather(req)
