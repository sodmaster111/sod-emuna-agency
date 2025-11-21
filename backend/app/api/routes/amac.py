from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import board_sim_client, cpao_client, executive_client
from app.services.executive_client import ExecServiceError

router = APIRouter(prefix="/amac", tags=["AMAC"])


class ExecDecisionRequest(BaseModel):
    question: str
    context: dict | None = None


class ExecDecisionResponse(BaseModel):
    decision: str
    reasoning_summary: str


class BoardSimRequest(BaseModel):
    proposal_id: str
    title: str
    description: str
    budget_ton: float | None = None
    tags: list[str] = Field(default_factory=list)


class BoardSimResponse(BaseModel):
    proposal_id: str
    summary: str
    final_stance: str
    opinions: list[dict]


class CPAOEvaluateRequest(BaseModel):
    actor: str
    action_type: str
    payload: dict


class CPAOEvaluateResponse(BaseModel):
    allowed: bool
    decision: str
    reasons: list[str]
    risk_level: str
    recommendations: list[str]


@router.post("/exec/decide", response_model=ExecDecisionResponse)
async def exec_decide(payload: ExecDecisionRequest) -> ExecDecisionResponse:
    try:
        result = executive_client.exec_decide(
            question=payload.question, context=payload.context
        )
    except ExecServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    return ExecDecisionResponse(
        decision=result.get("decision"),
        reasoning_summary=result.get("reasoning_summary"),
    )


@router.post("/board/simulate", response_model=BoardSimResponse)
async def board_simulate(payload: BoardSimRequest) -> BoardSimResponse:
    proposal_data = {
        "id": payload.proposal_id,
        "title": payload.title,
        "description": payload.description,
        "budget_ton": payload.budget_ton,
        "tags": payload.tags,
    }

    try:
        decision = board_sim_client.run_board_simulation(proposal_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return BoardSimResponse(
        proposal_id=decision.proposal_id,
        summary=decision.summary,
        final_stance=decision.final_stance,
        opinions=[opinion.model_dump() for opinion in decision.opinions],
    )


@router.post("/cpao/evaluate", response_model=CPAOEvaluateResponse)
async def cpao_evaluate(payload: CPAOEvaluateRequest) -> CPAOEvaluateResponse:
    cpao_input = cpao_client.build_cpao_input(
        actor=payload.actor,
        action_type=payload.action_type,
        payload=payload.payload,
    )
    judgement = cpao_client.cpao_evaluate(cpao_input)

    return CPAOEvaluateResponse(
        allowed=judgement.allowed,
        decision=judgement.decision,
        reasons=judgement.reasons,
        risk_level=judgement.risk_level,
        recommendations=judgement.recommendations,
    )
