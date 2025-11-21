"""In-process client for board meeting simulation."""

from langgraph_core.board_sim.schemas import BoardDecision, Proposal
from langgraph_core.board_sim.simulation import simulate_board_meeting


def run_board_simulation(proposal_data: dict) -> BoardDecision:
    """Run the board meeting simulation using provided proposal data."""

    proposal = Proposal(**proposal_data)
    return simulate_board_meeting(proposal)
