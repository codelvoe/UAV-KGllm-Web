from __future__ import annotations

from typing import Any

from services.data_loader import fusion_candidates
from services.fusion_engine import build_llm_prompt_payload, deterministic_llm_decision, generate_candidate_pool


def decide_candidate(candidate_id: str, scenario: str = "", local_rule_mode: bool = True) -> dict[str, Any]:
    item = _find_candidate(candidate_id, scenario)
    if not item:
        return {
            "candidate_id": candidate_id,
            "decision": "reject",
            "risk_level": "低",
            "reason": "未找到候选证据，系统默认拒绝。",
            "suggestion": "请检查候选编号或重新加载候选池。",
            "evidence": [],
        }
    decision = deterministic_llm_decision(item)
    decision["local_rule_mode"] = local_rule_mode
    decision["candidate_summary"] = _candidate_summary(item)
    return decision


def prompt_payload(candidate_id: str, scenario: str = "") -> dict[str, Any]:
    return build_llm_prompt_payload(candidate_id, scenario)


def _find_candidate(candidate_id: str, scenario: str = "") -> dict[str, Any]:
    return next(
        (row for row in generate_candidate_pool(scenario, 50) if row.get("candidate_id") == candidate_id),
        next((row for row in fusion_candidates() if row.get("candidate_id") == candidate_id), {}),
    )


def _candidate_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate.get("candidate_id"),
        "radar_track_id": candidate.get("radar_track_id"),
        "spectrum_track_id": candidate.get("spectrum_track_id"),
        "kg_score": candidate.get("kg_score"),
        "rank": candidate.get("rank"),
        "conflict_flag": candidate.get("conflict_flag"),
    }
