from fastapi import APIRouter
from pydantic import BaseModel

from services.chat_service import (
    append_message,
    call_ollama,
    create_session,
    delete_session as remove_session,
    get_sessions,
    ollama_status as check_ollama_status,
)

router = APIRouter()


class ChatBody(BaseModel):
    session_id: str = "chat_001"
    message: str
    context_type: str = ""
    context_id: str = ""
    model: str = ""


@router.post("/send")
def send(body: ChatBody):
    result = call_ollama(body.message, body.context_type, body.context_id, body.model)
    append_message(body.session_id, body.message, result["answer"], result)
    return {
        "session_id": body.session_id,
        "answer": result["answer"],
        "model": result.get("model"),
        "provider": result.get("provider"),
        "ok": result.get("ok"),
        "evidence": [
            {"type": "system", "field": "KG", "value": "53619 nodes / 105420 edges"},
            {
                "type": "method",
                "field": "strategies",
                "value": "Radar-only, KG Fusion, KG-Heuristic, KG+LLM Agent",
            },
        ],
        "suggested_questions": [
            "KG Fusion 在自然冲突场景下表现如何？",
            "缺失频谱时为什么需要 LLM 辅助？",
            "如何解释重复频谱去重？",
        ],
    }


@router.get("/sessions")
def sessions():
    return get_sessions()


@router.post("/new")
def new_session():
    return create_session()


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    return remove_session(session_id)


@router.get("/ollama-status")
def ollama_status():
    return check_ollama_status()
