"""AutoGen group chat representing the Sanhedrin council."""
from __future__ import annotations

from typing import Dict, List, Optional

from autogen import AssistantAgent, GroupChat, GroupChatManager

from app.core.engine import Engine


class SanhedrinCouncil:
    """Lazy-loaded AutoGen council using Ollama-backed agents."""

    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or Engine()
        self._agents: Optional[Dict[str, AssistantAgent]] = None

    def _build_agents(self) -> Dict[str, AssistantAgent]:
        """Instantiate the specialized assistant agents."""

        profiles = {
            "CEO": "CEO who finalizes decisions with 'APPROVED' when satisfied.",
            "CKO": "Chief Knowledge Officer focused on Torah ethics and risk controls.",
            "CFO": "Finance lead ensuring treasury growth and budget clarity.",
            "CMO": "Marketing officer focusing on outreach and growth tactics.",
        }
        return {
            name: AssistantAgent(
                name=name,
                system_message=f"You are the {name}. {profile}",
                llm_config=self.engine.llm_config,
            )
            for name, profile in profiles.items()
        }

    def _ensure_agents(self) -> None:
        if self._agents is None:
            self._agents = self._build_agents()

    def convene(self, topic: str = "Plan to increase the TON treasury") -> List[str]:
        """Run a group chat session until the CEO approves."""

        self._ensure_agents()
        group_chat = GroupChat(
            agents=list(self._agents.values()),
            messages=[],
            speaker_selection_method="auto",
            max_round=24,
            send_introductions=True,
            allow_repeat_speaker=False,
        )
        group_chat.termination_condition = self._termination_condition
        manager = GroupChatManager(
            groupchat=group_chat,
            llm_config=self.engine.llm_config,
            system_message=(
                "Facilitate the Digital Sanhedrin. Encourage short actionable updates and stop "
                "when the CEO responds with APPROVED."
            ),
        )
        group_chat.initiate_chat(manager, message=topic)
        return [msg["content"] for msg in group_chat.messages if isinstance(msg, dict)]

    @staticmethod
    def _termination_condition(messages: List[dict]) -> bool:
        if not messages:
            return False
        last = messages[-1]
        return last.get("name") == "CEO" and "APPROVED" in last.get("content", "").upper()
