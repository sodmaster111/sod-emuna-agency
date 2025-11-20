"""Simple orchestration layer for the Digital Sanhedrin agents."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from litellm import completion

from app.core.engine import Engine
from app.core.registry import REGISTRY
from app.models import AgentProfile, AgentTier


class SanhedrinOrchestrator:
    """Coordinate a round-table style debate across registered agents."""

    def __init__(self, *, engine: Optional[Engine] = None, registry: Optional[Dict[str, AgentProfile]] = None) -> None:
        self.engine = engine or Engine()
        self.registry = registry or REGISTRY

    def select_agents(
        self,
        *,
        agent_names: Optional[List[str]] = None,
        tiers: Optional[List[AgentTier]] = None,
        include_specialists: bool = False,
    ) -> List[AgentProfile]:
        """Resolve the list of active agents for a debate."""

        if agent_names:
            return [agent for name in agent_names if (agent := self.registry.get(name))]

        selected: Iterable[AgentProfile]
        if tiers:
            selected = [agent for agent in self.registry.values() if agent.tier in tiers]
        else:
            selected = [agent for agent in self.registry.values() if agent.tier == AgentTier.C_LEVEL]

        if include_specialists:
            selected = [
                *selected,
                *[agent for agent in self.registry.values() if agent.tier == AgentTier.SPECIALIST],
            ]

        # Ensure deterministic ordering and uniqueness by name
        unique = {}
        for agent in selected:
            unique[agent.name] = agent
        return list(unique.values())

    def debate(
        self,
        task: str,
        *,
        agent_names: Optional[List[str]] = None,
        tiers: Optional[List[AgentTier]] = None,
        include_specialists: bool = False,
    ) -> Dict[str, Any]:
        """Simulate a round-table discussion and return the synthesized outcome."""

        participants = self.select_agents(
            agent_names=agent_names,
            tiers=tiers,
            include_specialists=include_specialists,
        )
        if not participants:
            raise ValueError("No agents available for the requested debate configuration.")

        turns = [self._ask_agent(agent, task) for agent in participants]
        summary = self._summarize(task, turns)

        return {
            "task": task,
            "participants": [agent.name for agent in participants],
            "transcripts": turns,
            "summary": summary,
        }

    def _ask_agent(self, agent: AgentProfile, task: str) -> Dict[str, str]:
        """Collect a single agent opinion using the configured LLM."""

        messages = [
            {"role": "system", "content": agent.system_prompt},
            {
                "role": "user",
                "content": (
                    "You are participating in a Digital Sanhedrin round table. "
                    f"Given the task: {task}. Provide a concise recommendation with rationale."
                ),
            },
        ]
        content = self._complete(messages)
        return {"agent": agent.name, "role": agent.role, "content": content}

    def _summarize(self, task: str, turns: List[Dict[str, str]]) -> str:
        """Summarize the debate into an actionable outcome."""

        debate_digest = "\n".join(
            f"{turn['agent']}: {turn['content']}" for turn in turns
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are the facilitator of the Digital Sanhedrin. Merge the debate into an "
                    "actionable plan with clear next steps and any halachic caveats."
                ),
            },
            {"role": "user", "content": f"Task: {task}\nDebate:\n{debate_digest}"},
        ]
        return self._complete(messages)

    def _complete(self, messages: List[Dict[str, str]]) -> str:
        """Invoke LiteLLM with a safe fallback when the model is unavailable."""

        try:
            response = completion(
                model=self.engine.model,
                api_base=self.engine.ollama_base_url,
                api_key=self.engine.api_key or None,
                messages=messages,
            )
            choice = response["choices"][0]["message"]["content"]
            return choice.strip()
        except Exception:
            # Offline fallback: combine the messages into a readable note.
            user_message = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
            system_message = next((msg["content"] for msg in messages if msg["role"] == "system"), "")
            return f"[Simulated Response] {system_message}\n{user_message}"
