from __future__ import annotations

from typing import Dict

from telegram_gateway.config import get_settings


class ChannelResolutionError(LookupError):
    """Raised when a logical channel cannot be resolved to a chat ID."""


def resolve_chat_id(logical_channel: str) -> int:
    """Resolve a logical channel name to a Telegram chat ID.

    Args:
        logical_channel: The logical channel key, e.g. "telegram:luchamei_hashem".

    Raises:
        ChannelResolutionError: If no chat ID mapping is found.

    Returns:
        The configured chat ID.
    """

    settings = get_settings()
    mapping = settings.channels_map or {}
    try:
        chat_id = mapping[logical_channel]
    except KeyError as exc:
        raise ChannelResolutionError(
            f"No chat ID configured for logical channel '{logical_channel}'"
        ) from exc
    return chat_id


def list_known_channels() -> Dict[str, int]:
    """Return the configured logical-to-chat ID mapping."""

    settings = get_settings()
    return settings.channels_map or {}
