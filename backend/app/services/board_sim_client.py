from langgraph_core.board_sim.schemas import BoardDecision, Proposal
from langgraph_core.board_sim.simulation import simulate_board_meeting


def run_board_simulation(proposal_data: dict) -> BoardDecision:
    """Build a proposal model and run the board simulation."""

    proposal = Proposal(**proposal_data)
    return simulate_board_meeting(proposal)
