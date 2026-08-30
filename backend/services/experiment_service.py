from __future__ import annotations

from typing import Any

from services.data_loader import experiment_rows


def detection_results() -> list[dict[str, Any]]:
    return experiment_rows()


def efficiency_results() -> list[dict[str, Any]]:
    rows = experiment_rows()
    return [
        {
            "场景": _field(row, "场景", "鍦烘櫙"),
            "方法": _field(row, "方法", "鏂规硶"),
            "Token成本": _field(row, "Token成本", "Token鎴愭湰") or 0,
            "端到端延迟秒": _field(row, "端到端延迟秒", "绔埌绔欢杩熺") or 0,
        }
        for row in rows
    ]


def robustness_results() -> list[dict[str, Any]]:
    rows = experiment_rows()
    scenes = ["缺失频谱", "缺失视觉", "仅雷达", "缂哄け棰戣氨", "缂哄け瑙嗚", "浠呴浄杈?"]
    normalized = []
    seen = set()
    for scene in scenes:
        display = _scene_display(scene)
        if display in seen:
            continue
        seen.add(display)
        normalized.append(
            {
                "缺失场景": display,
                "KG Fusion F1": _f1(rows, scene, "KG Fusion"),
                "KG-Heuristic F1": _f1(rows, scene, "KG-Heuristic"),
                "KG+LLM F1": _f1(rows, scene, "KG+LLM Agent"),
                "F1保持率": _f1(rows, scene, "KG+LLM Agent"),
            }
        )
    return normalized[:3]


def performance_summary() -> dict[str, Any]:
    rows = experiment_rows()
    f1_values = [float(row.get("F1") or 0) for row in rows]
    far_values = [float(row.get("FAR") or 0) for row in rows]
    return {
        "scenario_count": len({_field(row, "场景", "鍦烘櫙") for row in rows}),
        "method_count": len({_field(row, "方法", "鏂规硶") for row in rows}),
        "best_f1": max(f1_values or [0]),
        "max_far": max(far_values or [0]),
    }


def _field(row: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in row:
            return row[name]
    return None


def _f1(rows: list[dict[str, Any]], scene: str, method: str) -> float:
    for row in rows:
        if _field(row, "场景", "鍦烘櫙") == scene and _field(row, "方法", "鏂规硶") == method:
            return float(row.get("F1") or 0)
    return 0.0


def _scene_display(scene: str) -> str:
    mapping = {
        "缂哄け棰戣氨": "缺失频谱",
        "缂哄け瑙嗚": "缺失视觉",
        "浠呴浄杈?": "仅雷达",
    }
    return mapping.get(scene, scene)
