"""TON treasury tools using TonTools and tonutils.

This module provides a lightweight async wrapper around TonTools wallet
operations to support basic treasury functions (generate wallet, check
balance, and send TON).
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

# Primary TON client/wallet utilities. Commented fallback if unavailable in env.
try:  # pragma: no cover - library import guard
    from TonTools import TonCenterClient, Wallet, mnemonic_new
except ImportError:  # pragma: no cover - optional dependency
    TonCenterClient = None  # type: ignore
    Wallet = None  # type: ignore
    mnemonic_new = None  # type: ignore
    # TonTools not installed. Install with `pip install TonTools` to enable live usage.

try:  # pragma: no cover - library import guard
    from tonutils import mnemonic as tonutils_mnemonic
except ImportError:  # pragma: no cover - optional dependency
    tonutils_mnemonic = None  # type: ignore
    # tonutils not installed. Install with `pip install tonutils` for mnemonic helpers.


@dataclass
class TonTreasury:
    """Async helper for TON treasury operations.

    Attributes:
        provider: TonCenterClient instance configured for the selected network.
        wallet: Wallet instance bound to the provider.
        seed_phrase: Raw seed phrase used to derive the wallet (if available).
    """

    provider: Any
    wallet: Any
    seed_phrase: Optional[str] = None

    # ---------------------------------------------------------------------
    # Factory methods
    # ---------------------------------------------------------------------
    @classmethod
    async def from_env(cls) -> "TonTreasury":
        """Instantiate a treasury using environment variables.

        Reads ``TON_WALLET_SEED`` or ``TON_PRIVATE_KEY`` and initializes a
        TonTools wallet bound to the mainnet provider. ``TON_PROVIDER_URL``
        controls the TonCenter endpoint and ``TON_NETWORK`` defaults to
        ``mainnet``.
        """

        provider_url = os.getenv("TON_PROVIDER_URL", "https://toncenter.com/api/v2/")
        network = os.getenv("TON_NETWORK", "mainnet")
        seed_phrase = os.getenv("TON_WALLET_SEED")
        private_key = os.getenv("TON_PRIVATE_KEY")

        provider = await cls._create_provider(provider_url=provider_url, network=network)

        if seed_phrase:
            wallet = await cls._wallet_from_seed(provider, seed_phrase)
        elif private_key:
            wallet = await cls._wallet_from_private_key(provider, private_key)
        else:
            raise ValueError("Set TON_WALLET_SEED or TON_PRIVATE_KEY in the environment")

        return cls(provider=provider, wallet=wallet, seed_phrase=seed_phrase)

    @classmethod
    async def generate_wallet(
        cls, provider_url: str = "https://toncenter.com/api/v2/", network: str = "mainnet"
    ) -> "TonTreasury":
        """Generate a fresh wallet with a new seed phrase.

        Returns a ``TonTreasury`` instance seeded with the generated mnemonic.
        """

        seed_phrase = await cls._generate_mnemonic()
        provider = await cls._create_provider(provider_url=provider_url, network=network)
        wallet = await cls._wallet_from_seed(provider, seed_phrase)
        return cls(provider=provider, wallet=wallet, seed_phrase=seed_phrase)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def get_address(self) -> str:
        """Return the wallet address as a user-friendly string."""

        try:
            address = await asyncio.to_thread(self._resolve_address)
            return str(address)
        except Exception as exc:  # pragma: no cover - runtime defensive path
            raise RuntimeError(f"Failed to resolve address: {exc}") from exc

    async def get_balance(self) -> float:
        """Return the wallet balance in TON."""

        try:
            balance = await asyncio.to_thread(self.wallet.get_balance)
            return float(balance)
        except Exception as exc:  # pragma: no cover - runtime defensive path
            raise RuntimeError(f"Failed to fetch balance: {exc}") from exc

    async def send(
        self, to_address: str, amount: float, message: Optional[str] = None
    ) -> Dict[str, Optional[Any]]:
        """Send TON to ``to_address``.

        Returns a dictionary containing transaction metadata: ``tx_hash``,
        ``status``, and ``block`` (where available from the underlying client).
        """

        try:
            result = await asyncio.to_thread(
                self.wallet.transfer_toncoins,
                destination_address=to_address,
                amount=amount,
                message=message,
            )
            return self._normalize_tx_result(result)
        except Exception as exc:  # pragma: no cover - runtime defensive path
            return {"tx_hash": None, "status": f"error: {exc}", "block": None}

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    @staticmethod
    async def _create_provider(provider_url: str, network: str) -> Any:
        """Initialize the TonCenter client for the requested network."""

        if TonCenterClient is None:  # pragma: no cover - optional dependency guard
            raise ImportError("TonTools is required for provider creation")

        # TonCenterClient is synchronous; wrap in a thread to keep API async-friendly.
        return await asyncio.to_thread(TonCenterClient, base_url=provider_url, network=network)

    @staticmethod
    async def _wallet_from_seed(provider: Any, seed_phrase: str | Sequence[str]) -> Any:
        if Wallet is None:  # pragma: no cover - optional dependency guard
            raise ImportError("TonTools is required for wallet creation")

        mnemonics: Sequence[str]
        if isinstance(seed_phrase, str):
            mnemonics = seed_phrase.split()
        else:
            mnemonics = list(seed_phrase)

        return await asyncio.to_thread(Wallet, provider=provider, mnemonics=mnemonics)

    @staticmethod
    async def _wallet_from_private_key(provider: Any, private_key: str) -> Any:
        if Wallet is None:  # pragma: no cover - optional dependency guard
            raise ImportError("TonTools is required for wallet creation")

        # Wallet accepts the ``private_key`` keyword for importing existing keys.
        return await asyncio.to_thread(Wallet, provider=provider, private_key=private_key)

    @staticmethod
    async def _generate_mnemonic() -> str:
        """Create a new mnemonic using TonTools or tonutils."""

        if mnemonic_new is not None:
            words = await asyncio.to_thread(mnemonic_new)
            phrase = " ".join(words) if isinstance(words, (list, tuple)) else str(words)
            return phrase

        if tonutils_mnemonic is not None and hasattr(tonutils_mnemonic, "mnemonic_new"):
            words = await asyncio.to_thread(tonutils_mnemonic.mnemonic_new)
            phrase = " ".join(words) if isinstance(words, (list, tuple)) else str(words)
            return phrase

        raise ImportError("Neither TonTools nor tonutils mnemonic generators are available")

    def _resolve_address(self) -> str:
        if hasattr(self.wallet, "address"):
            return str(self.wallet.address)
        if hasattr(self.wallet, "get_address"):
            return str(self.wallet.get_address())
        raise AttributeError("Wallet does not expose an address accessor")

    @staticmethod
    def _normalize_tx_result(result: Any) -> Dict[str, Optional[Any]]:
        """Normalize transaction data into a consistent dict."""

        if isinstance(result, dict):
            tx_hash = result.get("transaction_hash") or result.get("txHash") or result.get("tx_hash")
            block = result.get("block") or result.get("lt")
        else:
            tx_hash = getattr(result, "transaction_hash", None) or getattr(result, "txHash", None)
            block = getattr(result, "block", None) or getattr(result, "lt", None)

        status = "success" if tx_hash else "submitted"
        return {"tx_hash": tx_hash, "status": status, "block": block}


if __name__ == "__main__":
    async def _demo() -> None:
        treasury = await TonTreasury.from_env()
        address = await treasury.get_address()
        balance = await treasury.get_balance()
        print(f"Wallet address: {address}")
        print(f"Balance: {balance} TON")

    asyncio.run(_demo())
