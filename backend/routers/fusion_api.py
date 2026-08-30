from fastapi import APIRouter

from services.fusion_service import (
    explain_candidate,
    generate_candidates,
    get_candidate_detail,
    get_ranked_candidates,
    get_score_breakdown,
    get_statistics,
    list_candidates,
)

router = APIRouter()


@router.get("/candidates")
def candidates(scenario: str = ""):
    return list_candidates(scenario)


@router.get("/generated-candidates")
def generated_candidates(scenario: str = "", top_k: int = 10):
    return generate_candidates(scenario, top_k)


@router.get("/statistics")
def statistics(scenario: str = ""):
    return get_statistics(scenario)


@router.get("/ranked")
def ranked(scenario: str = "", top_k: int = 10):
    return get_ranked_candidates(scenario, top_k)


@router.get("/candidates/{candidate_id}")
def candidate_detail(candidate_id: str):
    return get_candidate_detail(candidate_id)


@router.get("/score-breakdown/{candidate_id}")
def score_breakdown(candidate_id: str):
    return get_score_breakdown(candidate_id)


@router.get("/explain/{candidate_id}")
def explain(candidate_id: str, scenario: str = ""):
    return explain_candidate(candidate_id, scenario)
