from langgraph_core.cpao.evaluator import CPAOEvaluator
from langgraph_core.cpao.schemas import CPAOInput, CPAOJudgement


evaluator = CPAOEvaluator()


def build_cpao_input(actor: str, action_type: str, payload: dict) -> CPAOInput:
    """Construct a CPAOInput payload for evaluation."""

    return CPAOInput(actor=actor, action_type=action_type, payload=payload)


def cpao_evaluate(inp: CPAOInput) -> CPAOJudgement:
    """Evaluate an action under the CPAO constitution."""

    return evaluator.evaluate(inp)
