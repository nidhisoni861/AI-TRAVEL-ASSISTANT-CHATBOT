from fastapi import APIRouter, Request, HTTPException
from app.models.schemas import ItineraryRequest, ItineraryResponse

router = APIRouter(prefix="/itinerary", tags=["itinerary"])


@router.post("", response_model=ItineraryResponse)
async def generate_itinerary(req: ItineraryRequest, request: Request):
    llm = request.app.state.llm
    if not llm or not llm.ready:
        raise HTTPException(503, "LLM service not ready")
    return await llm.generate_itinerary(req)
