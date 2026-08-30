from __future__ import annotations

from datetime import datetime
from typing import Any

from services.data_loader import DATA_DIR, OUTPUT_DIR, read_json, write_json


DRAFT_PATH = DATA_DIR / "report_draft.json"


def add_report_item(item: dict[str, Any]) -> dict[str, Any]:
    draft = get_report_draft()
    draft.setdefault("items", []).append(item)
    write_json(DRAFT_PATH, draft)
    return {"success": True, "draft": draft}


def get_report_draft() -> dict[str, Any]:
    return read_json(DRAFT_PATH, {"items": []})


def generate_report() -> dict[str, Any]:
    draft = get_report_draft()
    name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = OUTPUT_DIR / name
    lines = [
        "# 无人机多源感知融合研判报告",
        "",
        "## 数据概况",
        "当前数据包含雷达、频谱、视觉识别、光电状态和隐藏评价标签。",
        "",
    ]
    for item in draft.get("items", []):
        lines.extend([f"## {item.get('title', '研判条目')}", str(item.get("content", "")), ""])
    lines.extend(["## 处置建议", "建议对高风险 confirm 候选持续跟踪，对冲突候选保持人工确认。"])
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"success": True, "report_path": str(path)}


def clear_report_draft() -> dict[str, bool]:
    write_json(DRAFT_PATH, {"items": [], "title": "无人机多源融合研判报告"})
    return {"success": True}
