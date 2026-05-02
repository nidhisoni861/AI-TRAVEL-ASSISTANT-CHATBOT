from fastapi import APIRouter
from app.models.schemas import (
    FlightSearchRequest,
    FlightSearchResponse,
    BookingRequest,
    BookingResponse,
)
from app.services import amadeus_service, booking_service

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(req: FlightSearchRequest):
    return await amadeus_service.search_flights(req)


@router.post("/book", response_model=BookingResponse)
async def book_flight(req: BookingRequest):
    return booking_service.simulate_booking(req)
