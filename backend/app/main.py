import sys
import pathlib
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.routers import chat, flights, weather, places, itinerary, health
from app.routers import history
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

# Allow importing database.py from backend root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise database tables
    try:
        from database import init_db
        init_db()
        logger.info("SQLite database initialised")
    except Exception as e:
        logger.warning(f"Database init failed (non-fatal): {e}")

    settings = get_settings()
    logger.info("Starting AI Travel Assistant backend")
    logger.info(f"Base model: {settings.base_model}")
    logger.info(f"LoRA adapter: {settings.lora_adapter_path or '(none)'}")
    logger.info(f"HF Inference API mode: {settings.use_hf_inference_api}")

    app.state.rag = RAGService(persist_dir=settings.chroma_dir)
    app.state.rag.initialize()

    app.state.llm = LLMService(settings=settings, rag=app.state.rag)
    app.state.llm.initialize()

    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AI Travel Assistant Chatbot",
        description="Fine-tuned Gemma 2B (QLoRA) + RAG + real-time travel APIs",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        # Also accept any localhost / 127.0.0.1 port — Next.js frequently
        # falls back to 3001/3002/3003 when 3000 is taken.
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(flights.router)
    app.include_router(weather.router)
    app.include_router(places.router)
    app.include_router(itinerary.router)
    app.include_router(history.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    s = get_settings()
    uvicorn.run("app.main:app", host=s.app_host, port=s.app_port, reload=True)
