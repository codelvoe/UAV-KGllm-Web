from __future__ import annotations

from typing import Any

import requests

from services.data_loader import DATA_DIR, read_json, write_json


def load_chat_settings() -> dict[str, Any]:
    return read_json(DATA_DIR / "settings.json", {})


def build_system_context() -> str:
    return """
你是“基于知识图谱与大模型的无人机多源感知融合分析系统 V1.0”的对话助手。
你既可以回答系统项目相关问题，也可以进行正常沟通、解释概念、帮助用户组织表达、给出下一步建议。

回答风格：
- 中文为主，表达自然，不要像固定模板；
- 用户问简单问题时，直接回答，例如“1+1等于几”应回答“2”；
- 用户问“你是谁”时，可以先说明你是系统内的对话助手，再补充你也可以进行普通交流；
- 不要每次都机械复述系统背景；
- 不要把所有问题强行套回无人机项目；
- 用户问项目相关问题时，再优先结合下方项目上下文；
- 不确定时说明不确定，不要编造实时传感器输入。

项目上下文：
- radar tracks: 294，主要为空间/运动候选，虚警较多；
- spectrum tracks: 2，提供 DJI Air3 / drone 等无线电语义证据；
- recognize tracks: 24，提供视觉辅助证据；
- decrypt label tracks: 1，仅用于评价，不进入 KG 候选生成或 LLM 裁决；
- global KG: 53619 nodes / 105420 edges；
- 关键方法：Radar-only、KG Fusion、KG-Heuristic、KG+LLM Agent；
- 关键场景：Natural-conflict、模态缺失、重复频谱；
- Natural-conflict 中存在 radar bird/unknown 与 spectrum drone 的语义冲突；
- 诊断结论：真实候选 C02 已进入 KG 候选池和 LLM Top-K，但在 LLM 裁决阶段被 reject；C01 为误保留竞争候选。

事实边界：
1. 不要编造新的实时传感器输入；
2. 不要声称 decrypt 标签进入 KG 候选生成或 LLM 裁决；
3. 项目数据中没有依据时，要说“当前数据未显示”或“不确定”；
4. 普通交流、数学计算、解释术语、页面优化、写作建议等问题可以正常回答，不必强行套回项目。
""".strip()


def build_prompt(message: str, context_type: str = "", context_id: str = "") -> str:
    return (
        f"{build_system_context()}\n\n"
        f"当前上下文类型：{context_type or 'general'}\n"
        f"当前上下文编号：{context_id or '-'}\n"
        f"用户问题：{message}\n\n"
        "请用中文自然回答："
    )


def call_ollama(message: str, context_type: str = "", context_id: str = "", model: str = "") -> dict[str, Any]:
    settings = load_chat_settings()
    url = settings.get("ollama_url") or "http://localhost:11434/api/generate"
    model_name = model or settings.get("ollama_model") or "deepseek-r1:8b"
    payload = {
        "model": model_name,
        "prompt": build_prompt(message, context_type, context_id),
        "stream": False,
        "options": {"temperature": 0.35, "top_p": 0.9},
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return {
            "ok": True,
            "answer": data.get("response", "").strip() or "模型未返回有效内容。",
            "model": model_name,
            "provider": "ollama",
            "raw_eval_count": data.get("eval_count"),
            "raw_prompt_eval_count": data.get("prompt_eval_count"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "answer": f"本地 Ollama 调用失败：{exc}。请确认 Ollama 已启动、模型已拉取，并检查系统设置中的接口地址。",
            "model": model_name,
            "provider": "ollama",
            "error": str(exc),
        }


def append_message(session_id: str, user_message: str, assistant_answer: str, model_info: dict[str, Any]) -> None:
    sessions = read_json(DATA_DIR / "chat_sessions.json", [])
    session = next((item for item in sessions if item["session_id"] == session_id), None)
    if not session:
        session = {"session_id": session_id, "title": compact_title(user_message), "messages": []}
        sessions.append(session)
    if not session.get("title") or session.get("title") == "新建对话":
        session["title"] = compact_title(user_message)
    session.setdefault("messages", [])
    session["messages"].append({"role": "user", "content": user_message})
    session["messages"].append(
        {
            "role": "assistant",
            "content": assistant_answer,
            "model": model_info.get("model"),
            "provider": model_info.get("provider"),
            "ok": model_info.get("ok"),
        }
    )
    write_json(DATA_DIR / "chat_sessions.json", sessions)


def get_sessions() -> list[dict[str, Any]]:
    return read_json(DATA_DIR / "chat_sessions.json", [])


def create_session() -> dict[str, Any]:
    sessions = get_sessions()
    sid = f"chat_{len(sessions) + 1:03d}"
    item = {"session_id": sid, "title": "新建对话", "messages": []}
    sessions.append(item)
    write_json(DATA_DIR / "chat_sessions.json", sessions)
    return item


def delete_session(session_id: str) -> dict[str, bool]:
    sessions = [item for item in get_sessions() if item["session_id"] != session_id]
    write_json(DATA_DIR / "chat_sessions.json", sessions)
    return {"success": True}


def ollama_status() -> dict[str, Any]:
    settings = load_chat_settings()
    url = (settings.get("ollama_url") or "http://localhost:11434/api/generate").replace(
        "/api/generate", "/api/tags"
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        models = [item.get("name") for item in data.get("models", [])]
        return {"connected": True, "url": url, "models": models}
    except Exception as exc:
        return {"connected": False, "url": url, "models": [], "error": str(exc)}


def compact_title(message: str) -> str:
    text = message.strip().replace("\n", " ")
    return text[:18] or "新建对话"
