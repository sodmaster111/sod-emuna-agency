"""TON blockchain utility wrapper."""
from __future__ import annotations

from typing import Any, Dict


class TonWalletTool:
    """Minimal wrapper around tonutils wallet operations."""

    def __init__(self, mnemonic: str | None = None) -> None:
        self.mnemonic = mnemonic

    def get_balance(self, address: str) -> float:
        from tonutils.wallet import Wallet

        wallet = Wallet.from_mnemonic(self.mnemonic) if self.mnemonic else Wallet.from_address(address)
        return float(wallet.balance())

    def mint_nft(self, metadata: Dict[str, Any]) -> str:
        from tonutils.nft import NFTCollection

        collection = NFTCollection.from_mnemonic(self.mnemonic)
        result = collection.mint(metadata)
        return str(result)
