"""Group deliberation utilities for the Digital Sanhedrin."""
from __future__ import annotations

from typing import Dict, List

from autogen import AssistantAgent, GroupChat, GroupChatManager

from app.agents.registry import build_sanhedrin


class SanhedrinCouncil:
    """Encapsulates the GroupChat and meeting protocol."""

    def __init__(self, agents: Dict[str, AssistantAgent] | None = None) -> None:
        self.agents = agents or build_sanhedrin()
        self.group_chat = GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            speaker_selection_method="auto",
            max_round=30,
            send_introductions=True,
            allow_repeat_speaker=False,
        )
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.agents["CEO"].llm_config,
            system_message=(
                "Facilitate the Digital Sanhedrin board meeting. Ensure the CKO checks ethics. "
                "When the CEO responds with 'APPROVED', terminate the meeting and return the plan."
            ),
        )

    def convene(self, topic: str = "How to increase TON balance?") -> List[str]:
        """Run the board meeting until the CEO signals approval."""

        termination = self._termination_condition
        self.group_chat.termination_condition = termination
        self.group_chat.initiate_chat(self.manager, message=topic)
        return [msg["content"] for msg in self.group_chat.messages if isinstance(msg, dict)]

    @staticmethod
    def _termination_condition(messages: List[dict]) -> bool:
        """Stop when the CEO says APPROVED."""

        if not messages:
            return False
        last = messages[-1]
        return last.get("name") == "CEO" and "APPROVED" in last.get("content", "").upper()
