"""In-process client for the CPAO evaluator."""

from langgraph_core.cpao.evaluator import CPAOEvaluator
from langgraph_core.cpao.schemas import CPAOInput, CPAOJudgement

_cpao = CPAOEvaluator()


def build_cpao_input(actor: str, action_type: str, payload: dict) -> CPAOInput:
    """Helper to construct a ``CPAOInput`` object."""

    return CPAOInput(actor=actor, action_type=action_type, payload=payload)


def cpao_evaluate(inp: CPAOInput) -> CPAOJudgement:
    """Evaluate an action using the CPAO evaluator."""

    return _cpao.evaluate(inp)


def cpao_is_allowed(inp: CPAOInput) -> bool:
    """Check if the action is allowed based on CPAO rules."""

    return _cpao.is_allowed(inp)
