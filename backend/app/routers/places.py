from fastapi import APIRouter
from app.models.schemas import PlacesRequest, PlacesResponse
from app.services import places_service

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", response_model=PlacesResponse)
async def get_places(req: PlacesRequest):
    return await places_service.get_places(req)
