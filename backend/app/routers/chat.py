import sys
import pathlib
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models.schemas import ChatRequest, ChatResponse

# Allow importing database.py from backend root
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_db_optional():
    """Return a DB session if available, else None."""
    try:
        from database import SessionLocal
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception:
        yield None


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    llm = request.app.state.llm
    if not llm or not llm.ready:
        raise HTTPException(503, "LLM service not ready")

    response = await llm.chat(req)

    # Persist messages to SQLite (best-effort — never crash the chat endpoint)
    try:
        from database import SessionLocal, User, ChatMessage
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.session_id == req.session_id).first()
            if not user:
                user = User(session_id=req.session_id)
                db.add(user)
                db.commit()
                db.refresh(user)

            # Save user message
            db.add(ChatMessage(
                user_id    = user.id,
                session_id = req.session_id,
                role       = "user",
                content    = req.message,
            ))
            # Save assistant reply
            db.add(ChatMessage(
                user_id    = user.id,
                session_id = req.session_id,
                role       = "assistant",
                content    = response.reply,
                tool_calls = [tc.model_dump() for tc in response.tool_calls] if response.tool_calls else None,
                citations  = response.citations or None,
            ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass  # DB persistence is non-critical

    return response


@router.delete("/{session_id}")
async def reset_session(session_id: str, request: Request):
    request.app.state.llm.reset_session(session_id)
    return {"session_id": session_id, "status": "reset"}
