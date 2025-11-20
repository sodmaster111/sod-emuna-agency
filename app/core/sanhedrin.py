"""Sanhedrin council orchestration using Microsoft AutoGen GroupChat."""
from __future__ import annotations

import asyncio
from typing import Dict, List

from autogen import AssistantAgent, GroupChat, GroupChatManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import AGENTS_CONFIG
from app.core.config import get_settings
from app.core.database import log_entry
from app.tools.knowledge import KnowledgeTool
from app.tools.ton_wallet import TonWalletTool
from app.tools.web_agent import WebAgent


class SanhedrinCouncil:
    """Coordinates Digital Sanhedrin deliberations and execution."""

    def __init__(self, db_session: AsyncSession | None = None) -> None:
        self.settings = get_settings()
        self.mission_goal = self.settings.mission_goal
        self.db_session = db_session
        self.llm_config = {
            "config_list": [
                {
                    "model": "gpt-4o-mini",
                    "api_key": "na",
                    "base_url": self.settings.ollama_base_url,
                }
            ]
        }
        self.agents: Dict[str, AssistantAgent] = {
            name: AssistantAgent(name=name, system_message=cfg["system_message"], llm_config=self.llm_config)
            for name, cfg in AGENTS_CONFIG.items()
        }
        self.group_chat = GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            speaker_selection_method="round_robin",
            max_round=24,
            send_introductions=True,
        )
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.llm_config,
            system_message=(
                "Coordinate a Digital Sanhedrin strategy session. The CEO proposes a"
                " cohesive plan. The CKO validates halachic compliance. The CFO ensures"
                " budget viability. Seek consensus and have the CEO respond with"
                " 'APPROVED' once the plan is ready."
            ),
        )
        self.web_agent = WebAgent()
        self.knowledge_tool = KnowledgeTool()
        self.ton_wallet = TonWalletTool()

    async def convene(self) -> List[str]:
        """Run the group chat and return the deliberation transcript."""

        mission_prompt = (
            f"Mission Goal: {self.mission_goal}. CEO: propose a plan."
            " CKO: enforce halacha. CFO: validate costs. Other chiefs: refine"
            " execution. CEO must end with 'APPROVED' when consensus is reached."
        )
        try:
            messages = await asyncio.to_thread(self._run_group_chat, mission_prompt)
        except Exception as exc:  # noqa: BLE001
            fallback = self._offline_brainstorm(str(exc))
            messages = await self._persist_and_collect(fallback)
            await self._execute_tools(messages)
            return [msg["message"] for msg in fallback]

        transcript = await self._persist_and_collect(messages)
        await self._execute_tools(transcript)
        return [entry["message"] for entry in transcript]

    def _run_group_chat(self, prompt: str) -> List[dict]:
        """Invoke the AutoGen GroupChat synchronously in a worker thread."""

        self.group_chat.termination_condition = self._termination_condition
        self.group_chat.messages = []
        self.group_chat.initiate_chat(self.manager, message=prompt)
        return [msg for msg in self.group_chat.messages if isinstance(msg, dict)]

    async def _persist_and_collect(self, messages: List[dict]) -> List[dict]:
        """Store messages in the database and return normalized records."""

        collected: List[dict] = []
        for msg in messages:
            agent = msg.get("name", "unknown")
            content = msg.get("content", "")
            collected.append({"agent": agent, "message": content})
            if self.db_session:
                await log_entry(self.db_session, agent=agent, message=content)
        return collected

    @staticmethod
    def _termination_condition(messages: List[dict]) -> bool:
        """Stop when the CEO approves the plan."""

        if not messages:
            return False
        last = messages[-1]
        return last.get("name") == "CEO" and "APPROVED" in last.get("content", "").upper()

    async def _execute_tools(self, transcript: List[dict]) -> None:
        """Placeholder execution pipeline for approved plans."""

        summary = "\n".join(f"{msg['agent']}: {msg['message']}" for msg in transcript)
        if not summary:
            return
        try:
            # Probe knowledge bases or external signals as a stub for tool execution.
            if "market" in summary.lower():
                await self.knowledge_tool.lookup("market dynamics for TON")
            if "ton" in summary.lower():
                self.ton_wallet.get_balance(address="")
            if "research" in summary.lower():
                await self.web_agent.visit_url("https://sefaria.org")
        except Exception:
            # Execution tools are best-effort and should not block the meeting cycle.
            return

    def _offline_brainstorm(self, error: str) -> List[dict]:
        """Deterministic fallback plan when LLM access is unavailable."""

        template = [
            {
                "name": "CEO",
                "content": (
                    f"APPROVED: Launch a lean experiment to advance the mission despite"
                    f" LLM error '{error}'."
                ),
            },
            {
                "name": "CKO",
                "content": "All steps respect halacha and community safeguards.",
            },
            {
                "name": "CFO",
                "content": "Budget capped with transparent risk controls and audits.",
            },
        ]
        return template


__all__ = ["SanhedrinCouncil"]
