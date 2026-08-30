from __future__ import annotations

from typing import Any

from services.data_loader import fusion_candidates
from services.fusion_engine import (
    candidate_explanation,
    candidate_statistics,
    generate_candidate_pool,
    rank_candidates,
)


def list_candidates(scenario: str = "") -> list[dict[str, Any]]:
    return fusion_candidates(scenario or None)


def generate_candidates(scenario: str = "", top_k: int = 10) -> list[dict[str, Any]]:
    return generate_candidate_pool(scenario, top_k)


def get_statistics(scenario: str = "") -> dict[str, Any]:
    return candidate_statistics(scenario)


def get_ranked_candidates(scenario: str = "", top_k: int = 10) -> list[dict[str, Any]]:
    return rank_candidates(generate_candidate_pool(scenario, top_k))


def get_candidate_detail(candidate_id: str) -> dict[str, Any]:
    return next((row for row in fusion_candidates() if row.get("candidate_id") == candidate_id), {})


def get_score_breakdown(candidate_id: str) -> dict[str, Any]:
    item = get_candidate_detail(candidate_id)
    return item.get("score_breakdown", {})


def explain_candidate(candidate_id: str, scenario: str = "") -> dict[str, Any]:
    item = next(
        (row for row in generate_candidate_pool(scenario, 50) if row.get("candidate_id") == candidate_id),
        {},
    )
    return candidate_explanation(item) if item else {}
