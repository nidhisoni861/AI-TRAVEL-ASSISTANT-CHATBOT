from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    return {"name": "AI Travel Assistant", "status": "ok", "docs": "/docs"}


@router.get("/health")
def health(request: Request):
    llm = getattr(request.app.state, "llm", None)
    return {
        "status": "ok",
        "llm_ready": bool(llm and llm.ready),
        "llm_mode": llm.mode if llm else "unknown",
    }
