from __future__ import annotations

from typing import Any

from services.data_loader import all_tracks


def list_tracks(source: str = "", target_type: str = "") -> list[dict[str, Any]]:
    rows = all_tracks(source or None)
    if target_type:
        rows = [row for row in rows if str(row.get("target_type", "")) == target_type]
    return rows


def get_track_detail(track_id: str) -> dict[str, Any]:
    return next((row for row in all_tracks() if row.get("track_id") == track_id), {"track_id": track_id})


def build_track_features(track_id: str) -> dict[str, Any]:
    row = get_track_detail(track_id)
    return {
        "radar": [
            {"name": "SNR", "value": row.get("snr_mean") or 0},
            {"name": "速度", "value": row.get("speed_mean") or 0},
            {"name": "高度", "value": row.get("altitude_mean") or 0},
            {"name": "点数", "value": row.get("point_count") or 0},
        ],
        "timeline": [
            {"time": row.get("start_time"), "event": "start"},
            {"time": row.get("end_time"), "event": "end"},
        ],
        "quality": explain_track_quality(row),
        "raw": row,
    }


def explain_track_quality(row: dict[str, Any]) -> list[dict[str, str]]:
    point_count = _num(row.get("point_count"))
    speed = _num(row.get("speed_mean"))
    snr = _num(row.get("snr_mean"))
    return [
        {
            "name": "连续性",
            "level": "high" if point_count >= 30 else "medium",
            "text": "轨迹点数较多，可形成稳定摘要。" if point_count >= 30 else "轨迹点数偏少，需要其他模态补充。",
        },
        {
            "name": "运动合理性",
            "level": "high" if 0 < speed <= 25 else "medium",
            "text": "速度处于可解释范围。" if 0 < speed <= 25 else "速度字段不足或偏离常规范围。",
        },
        {
            "name": "信号质量",
            "level": "high" if snr >= 12 else "medium" if snr > 0 else "unknown",
            "text": "SNR 可作为雷达可靠性证据。" if snr > 0 else "当前轨迹无 SNR 字段。",
        },
    ]


def _num(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0
