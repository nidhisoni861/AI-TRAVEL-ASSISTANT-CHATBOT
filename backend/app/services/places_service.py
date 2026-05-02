"""Google Places (Text Search). Falls back to mock if no key."""
import httpx
from loguru import logger

from app.config import get_settings
from app.models.schemas import PlacesRequest, PlacesResponse, Place


CATEGORY_QUERY = {
    "attractions": "tourist attractions in {loc}",
    "restaurants": "best restaurants in {loc}",
    "hotels": "hotels in {loc}",
    "events": "events in {loc}",
}


def _mock(req: PlacesRequest) -> PlacesResponse:
    samples = {
        "attractions": [
            ("Old Town Square", "Historic plaza with cafes and street performers."),
            ("National Museum", "Comprehensive collection of art and history."),
            ("Central Park", "Sprawling green space ideal for an afternoon stroll."),
            ("Cathedral", "Gothic landmark with panoramic tower views."),
            ("Riverside Promenade", "Scenic walking path along the river."),
            ("Modern Art Gallery", "Rotating contemporary exhibitions."),
        ],
        "restaurants": [
            ("Trattoria Bella", "Family-run spot famous for handmade pasta."),
            ("Sakura Sushi", "Omakase-style sushi counter, reservation only."),
            ("Le Petit Bistro", "Cozy French bistro with seasonal menu."),
            ("The Spice Route", "Upscale Indian with regional thalis."),
            ("Burger & Brews", "Craft burgers and a rotating tap list."),
            ("Vegan Garden", "Plant-based comfort food, popular brunch."),
        ],
        "hotels": [
            ("Grand Plaza Hotel", "5★ central with rooftop pool."),
            ("Boutique Maison", "Charming 4★ in a converted townhouse."),
            ("CityStay Inn", "Reliable mid-range, near transit."),
            ("Hostel Wanderer", "Backpacker-friendly with private rooms."),
        ],
        "events": [
            ("Summer Jazz Festival", "Open-air concerts in the main square."),
            ("Food Truck Friday", "Weekly street-food gathering."),
            ("Night Market", "Saturdays only, local crafts and street food."),
        ],
    }
    items = samples.get(req.category, samples["attractions"])[: req.limit]
    return PlacesResponse(
        location=req.location,
        is_mock=True,
        places=[
            Place(
                name=name,
                description=desc,
                rating=4.2 + (i % 7) / 10,
                category=req.category,
            )
            for i, (name, desc) in enumerate(items)
        ],
    )


async def get_places(req: PlacesRequest) -> PlacesResponse:
    s = get_settings()
    if not s.google_places_api_key:
        return _mock(req)

    query = CATEGORY_QUERY[req.category].format(loc=req.location)
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": s.google_places_api_key}

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception(f"Google Places failed, falling back: {e}")
        return _mock(req)

    places: list[Place] = []
    for r in data.get("results", [])[: req.limit]:
        photo_ref = (r.get("photos") or [{}])[0].get("photo_reference")
        image_url = (
            f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400"
            f"&photoreference={photo_ref}&key={s.google_places_api_key}"
            if photo_ref else None
        )
        places.append(Place(
            name=r.get("name", "Unknown"),
            address=r.get("formatted_address"),
            rating=r.get("rating"),
            price_level=r.get("price_level"),
            category=req.category,
            description=", ".join(r.get("types", [])[:3]),
            image_url=image_url,
        ))
    return PlacesResponse(location=req.location, places=places, is_mock=False)
