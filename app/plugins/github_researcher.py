"""GitHub research plugin for discovering projects from Awesome lists."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

import requests
from bs4 import BeautifulSoup
from semantic_kernel.functions import kernel_function


DEFAULT_AWESOME_LISTS: Sequence[str] = (
    "https://raw.githubusercontent.com/e2b-dev/awesome-ai-agents/HEAD/README.md",
    "https://raw.githubusercontent.com/f/awesome-chatgpt-prompts/HEAD/README.md",
)


@dataclass
class GitHubResearcher:
    """Native function set for exploring GitHub Awesome repositories."""

    keywords: Sequence[str] = field(
        default_factory=lambda: ["marketing", "telegram", "ton"]
    )
    report_path: Path = field(default_factory=lambda: Path("reports/tech_radar.md"))

    @kernel_function(
        name="search_github_awesome_lists",
        description="Search Awesome GitHub lists for projects matching keywords and save a tech radar report.",
    )
    async def search_github_awesome_lists(
        self,
        awesome_readmes: Sequence[str] | None = None,
        keywords: str | None = None,
    ) -> str:
        keyword_set = self._prepare_keywords(keywords)
        sources = list(awesome_readmes or DEFAULT_AWESOME_LISTS)
        findings: List[str] = []

        tasks = [asyncio.to_thread(self._fetch_readme, url) for url in sources]
        for content in await asyncio.gather(*tasks):
            findings.extend(self._extract_projects(content, keyword_set))

        if not findings:
            summary = "No projects matched the specified keywords."
        else:
            summary = f"Identified {len(findings)} matching projects."

        self._write_report(findings, keyword_set)
        return summary

    def _prepare_keywords(self, keywords: str | None) -> List[str]:
        if keywords:
            return [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
        return [kw.lower() for kw in self.keywords]

    def _fetch_readme(self, url: str) -> str:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return response.text

    def _extract_projects(self, content: str, keywords: Iterable[str]) -> List[str]:
        soup = BeautifulSoup(content, "html.parser")
        text_lines = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]
        matches: List[str] = []
        for line in text_lines:
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in keywords) and ("http" in lower_line or "github" in lower_line):
                matches.append(line)
        return matches

    def _write_report(self, findings: Sequence[str], keywords: Iterable[str]) -> None:
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Tech Radar", "", f"Filtered by keywords: {', '.join(keywords)}", ""]
        if findings:
            lines.append("## Matching Projects")
            lines.extend(f"- {item}" for item in findings)
        else:
            lines.append("No matching projects found.")
        self.report_path.write_text("\n".join(lines), encoding="utf-8")
