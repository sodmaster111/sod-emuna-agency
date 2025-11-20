"""TON wallet utility wrapper."""
from __future__ import annotations

import importlib.util
from typing import Optional

LiteClient = None
if importlib.util.find_spec("pytoniq"):
    from pytoniq import LiteClient  # type: ignore[assignment]


class TonWalletTool:
    """Minimal TON wallet helper (stub-friendly)."""

    def __init__(self, mnemonic: Optional[str] = None) -> None:
        self.mnemonic = mnemonic
        self.client = LiteClient() if LiteClient else None

    def get_balance(self, address: str) -> float:
        """Return the balance for an address (stubbed to 0 when offline)."""

        if not address or not self.client:
            return 0.0
        # In a full implementation, query the TON blockchain here.
        return float(self.client.get_balance(address))


__all__ = ["TonWalletTool"]
