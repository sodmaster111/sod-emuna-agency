"""TON finance plugin wallet manager."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from semantic_kernel.functions import kernel_function
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV4R2
from tonutils.wallet.messages import WalletMessage
from tonutils.wallet.utils import to_nano


@dataclass
class TransactionReceipt:
    """Lightweight transaction confirmation details."""

    tx_hash: str
    amount: float
    sender: Optional[str]
    comment: Optional[str]


class TonWalletManager:
    """Expose TON wallet operations to Semantic Kernel agents."""

    def __init__(
        self,
        mnemonic_env: str = "TON_WALLET_MNEMONIC",
        tonapi_key_env: str = "TONAPI_KEY",
        is_testnet: bool | str = False,
    ) -> None:
        self.mnemonic_env = mnemonic_env
        self.tonapi_key_env = tonapi_key_env
        self.is_testnet = str(is_testnet).lower() == "true"
        self._client: Optional[TonapiClient] = None
        self._wallet: Optional[WalletV4R2] = None

    @property
    def mnemonic(self) -> str:
        mnemonic_value = os.getenv(self.mnemonic_env, "")
        if not mnemonic_value:
            raise ValueError("TON wallet mnemonic is not set in the environment.")
        return mnemonic_value

    @property
    def client(self) -> TonapiClient:
        if self._client is None:
            api_key = os.getenv(self.tonapi_key_env, "")
            if not api_key:
                raise ValueError("TONAPI key is required for TonapiClient.")
            self._client = TonapiClient(api_key=api_key, is_testnet=self.is_testnet)
        return self._client

    @property
    def wallet(self) -> WalletV4R2:
        if self._wallet is None:
            self._wallet = WalletV4R2.from_mnemonic(self.client, self.mnemonic)
        return self._wallet

    @kernel_function(name="check_balance", description="Check TON wallet balance")
    async def check_balance(self, address: Optional[str] = None) -> float:
        """Return the TON balance for the provided or configured wallet address."""

        target_address = address or self.wallet.address.to_str()
        raw_balance = await self.client.get_account_balance(target_address)
        return float(raw_balance) / 1_000_000_000

    @kernel_function(name="send_ton", description="Send TON to a recipient address")
    async def send_ton(
        self,
        to_address: str,
        amount: float,
        comment: Optional[str] = None,
        send_mode: int = 3,
    ) -> str:
        """Transfer TON with an optional human-readable comment."""

        transfer_message: WalletMessage = self.wallet.create_wallet_internal_message(
            destination=to_address,
            value=to_nano(amount),
            body=comment,
            send_mode=send_mode,
        )
        tx_hash = await self.wallet.raw_transfer(messages=[transfer_message])
        return tx_hash

    @kernel_function(
        name="verify_transaction",
        description="Verify a TON transaction contains the expected payment comment",
    )
    async def verify_transaction(
        self,
        expected_comment: str,
        minimum_amount: float = 0.0,
        payer_address: Optional[str] = None,
        lookback: int = 20,
    ) -> Optional[Dict[str, Any]]:
        """Validate recent inbound payments by comment and amount."""

        address = self.wallet.address.to_str()
        result = await self.client._get(
            method=f"/blockchain/accounts/{address}/transactions",
            params={"limit": lookback},
        )
        for tx in result.get("transactions", []):
            inbound: Dict[str, Any] = tx.get("in_msg") or {}
            comment = inbound.get("message") or ""
            amount = float(inbound.get("value", 0)) / 1_000_000_000
            sender = inbound.get("source")

            if payer_address and sender != payer_address:
                continue
            if expected_comment and expected_comment not in comment:
                continue
            if amount < minimum_amount:
                continue

            return TransactionReceipt(
                tx_hash=tx.get("hash", ""),
                amount=amount,
                sender=sender,
                comment=comment,
            ).__dict__

        return None
