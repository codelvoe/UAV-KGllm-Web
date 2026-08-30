from __future__ import annotations

from typing import Any

from services.data_loader import all_tracks, experiment_rows
from services.fusion_engine import experiment_summary, modality_quality_report


def dashboard_summary() -> dict[str, Any]:
    return {
        "radar_tracks": 294,
        "spectrum_tracks": 2,
        "recognize_tracks": 24,
        "decrypt_labels": 1,
        "kg_nodes": 53619,
        "kg_edges": 105420,
        "time_range": "2026-04-14 12:46:30 ~ 13:04:15",
        "system_status": "running",
    }


def dashboard_charts() -> dict[str, Any]:
    rows = experiment_rows()
    return {
        "modal_records": [
            {"name": "radar", "value": 15362},
            {"name": "spectrum", "value": 445},
            {"name": "recognize", "value": 166},
            {"name": "pho_status", "value": 422},
            {"name": "decrypt", "value": 422},
        ],
        "f1_comparison": [
            row for row in rows if str(_field(row, "场景", "鍦烘櫙")) in {"完整模态", "瀹屾暣妯℃€?"}
        ],
        "far_comparison": [
            row for row in rows if _field(row, "方法", "鏂规硶") == "KG+LLM Agent"
        ],
        "recent": recent_decisions(),
        "track_total": len(all_tracks()),
    }


def recent_decisions() -> list[dict[str, str]]:
    return [
        {"time": "12:52:33", "title": "Natural-conflict 候选 C02 被拒绝", "level": "risk"},
        {"time": "12:53:32", "title": "重复频谱候选完成去重分析", "level": "normal"},
        {"time": "13:04:15", "title": "阶段性研判记录已生成", "level": "normal"},
    ]


def quality_summary() -> dict[str, Any]:
    return modality_quality_report()


def experiment_overview() -> dict[str, Any]:
    return experiment_summary()


def _field(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None
