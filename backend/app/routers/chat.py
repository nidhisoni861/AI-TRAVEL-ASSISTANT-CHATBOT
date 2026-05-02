from fastapi import APIRouter, Request, HTTPException
from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    llm = request.app.state.llm
    if not llm or not llm.ready:
        raise HTTPException(503, "LLM service not ready")
    return await llm.chat(req)


@router.delete("/{session_id}")
async def reset_session(session_id: str, request: Request):
    request.app.state.llm.reset_session(session_id)
    return {"session_id": session_id, "status": "reset"}
