from fastapi import APIRouter
from pydantic import BaseModel

from services.llm_service import decide_candidate, prompt_payload

router = APIRouter()


class DecisionBody(BaseModel):
    candidate_id: str
    scenario: str = "完整模态"
    local_rule_mode: bool = True


@router.post("/decision")
def decision(body: DecisionBody):
    return decide_candidate(body.candidate_id, body.scenario, body.local_rule_mode)


@router.get("/prompt/{candidate_id}")
def prompt(candidate_id: str, scenario: str = ""):
    return prompt_payload(candidate_id, scenario)
