from __future__ import annotations

from typing import Any

from services.data_loader import DATA_DIR, read_json, write_json


SETTINGS_PATH = DATA_DIR / "settings.json"


def get_settings() -> dict[str, Any]:
    return read_json(SETTINGS_PATH, default_settings())


def save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    merged = default_settings()
    merged.update(settings or {})
    write_json(SETTINGS_PATH, merged)
    return {"success": True, "settings": merged}


def default_settings() -> dict[str, Any]:
    return {
        "data_dir": "backend/data",
        "local_rule_llm": False,
        "ollama_url": "http://localhost:11434/api/generate",
        "ollama_model": "deepseek-r1:8b",
        "neo4j_enabled": False,
        "neo4j_uri": "bolt://localhost:7687",
        "neo4j_user": "neo4j",
        "neo4j_database": "neo4j",
        "top_k": 5,
        "kg_limit": 300,
        "yolo_model_path": "backend/services/yoloDetection/models/best.pt",
        "yolo_conf": 0.25,
        "frame_stride": 12,
        "device": "cpu",
        "save_prompt": True,
        "save_trace": True,
        "save_operation_log": True,
        "output_retention_days": 7,
    }
