"""Financial tools for interacting with the TON blockchain."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import uuid4

from pytoniq import Address, LiteClient, WalletV4R2

DEFAULT_LITE_ENDPOINT = "https://toncenter.com/api/v2/jsonRPC"


def _client(endpoint: str | None = None) -> LiteClient:
    """Create a LiteClient instance pointing at the desired endpoint."""

    return LiteClient.from_url(endpoint or DEFAULT_LITE_ENDPOINT)


def check_balance(address: str, endpoint: str | None = None) -> Decimal:
    """Return the balance (in TON) for the given address.

    Parameters
    ----------
    address:
        Wallet address to query.
    endpoint:
        Optional TON Center RPC endpoint.
    """

    client = _client(endpoint)
    account = client.get_account(Address(address))
    # TON balances are stored in nanocoins (1e9 = 1 TON)
    return Decimal(account.balance) / Decimal(1e9)


def send_ton(
    destination: str,
    amount: Decimal,
    mnemonic: list[str],
    endpoint: str | None = None,
    payload: Optional[Dict[str, Any]] = None,
) -> str:
    """Send TON from the wallet derived from the mnemonic to the destination.

    Parameters
    ----------
    destination:
        Recipient wallet address.
    amount:
        Amount in TON to send.
    mnemonic:
        24-word seed phrase for the sending wallet.
    endpoint:
        Optional TON Center RPC endpoint.
    payload:
        Optional dictionary payload to attach to the transfer.
    """

    client = _client(endpoint)
    wallet = WalletV4R2.from_mnemonic(mnemonic, client=client)
    transfer = wallet.create_transfer_message(
        destination=Address(destination),
        amount=int(amount * Decimal(1e9)),
        payload=payload,
    )
    result = wallet.send_message(transfer)
    return str(result)


def create_nft_invoice(
    buyer_address: str,
    amount: Decimal,
    description: str | None = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a placeholder NFT invoice payload for future Tact integration.

    This stub does not perform on-chain deployment. It only prepares the
    metadata structure and a deterministic invoice identifier so the calling
    agent can present a payable request to the CFO. Once the Tact contract is
    finalized, this helper should be updated to deploy the contract and return
    the live payment link/transaction hash.
    """

    invoice_id = f"nft-invoice-{uuid4()}"
    return {
        "invoice_id": invoice_id,
        "buyer": buyer_address,
        "amount_ton": str(amount),
        "description": description or "Soulbound NFT invoice",
        "metadata": metadata or {},
        "status": "pending-signature",
        "note": "Tact deployment pending; this payload is off-chain only.",
    }


def mint_soulbound_nft(
    owner_address: str,
    metadata: dict[str, Any],
    mnemonic: list[str] | None = None,
) -> str:
    """Stub for minting a soulbound NFT using Tact contract logic.

    This function is intentionally left as a stub so it can be wired to the
    on-chain Tact contract once deployment details are finalized.
    """

    _ = (owner_address, metadata, mnemonic)
    return "soulbound NFT minting is not yet implemented"
