"""Translation utilities for generated and imported content."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Provide async translation helpers with chunking safeguards."""

    def __init__(self, *, max_chunk_size: int = 2048):
        self.max_chunk_size = max_chunk_size

    async def translate_he_to_ru(self, text: str) -> str:
        """Translate Hebrew text to Russian.

        Currently returns the original text. TODO: integrate external LLM or orchestrator.
        """

        logger.debug("Starting Hebrew->Russian translation (%s chars)", len(text))
        return await self._translate_text(text, target_lang="ru")

    async def translate_he_to_en(self, text: str) -> str:
        """Translate Hebrew text to English.

        Currently returns the original text. TODO: integrate external LLM or orchestrator.
        """

        logger.debug("Starting Hebrew->English translation (%s chars)", len(text))
        return await self._translate_text(text, target_lang="en")

    async def batch_translate(self, items: list[str], target_lang: str) -> list[str]:
        """Translate a list of items to the requested language."""

        logger.info("Translating %s items to %s", len(items), target_lang)
        results: list[str] = []
        for index, item in enumerate(items, start=1):
            logger.debug("Translating item %s/%s (%s chars)", index, len(items), len(item))
            results.append(await self._translate_text(item, target_lang=target_lang))
        return results

    async def _translate_text(self, text: str, *, target_lang: str) -> str:
        if not text:
            return ""

        chunks = self._chunk_text(text)
        logger.debug("Split text into %s chunk(s) for %s translation", len(chunks), target_lang)

        translated_chunks = []
        for idx, chunk in enumerate(chunks, start=1):
            logger.debug(
                "Translating chunk %s/%s to %s (len=%s)", idx, len(chunks), target_lang, len(chunk)
            )
            translated_chunks.append(await self._translate_chunk(chunk, target_lang=target_lang))

        return "".join(translated_chunks)

    def _chunk_text(self, text: str) -> list[str]:
        if len(text) <= self.max_chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.max_chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            start = end

        logger.info("Chunked long text into %s segments (max=%s)", len(chunks), self.max_chunk_size)
        return chunks

    async def _translate_chunk(self, text: str, *, target_lang: str) -> str:
        """Placeholder chunk translation.

        TODO: integrate external LLM or orchestrator.
        """

        logger.debug("Translating chunk to %s (len=%s)", target_lang, len(text))
        return text
