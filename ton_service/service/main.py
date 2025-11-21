import base64
import logging
import os
import sys
from typing import Optional

import requests
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

try:
    from tonsdk.contract.wallet import Wallets, WalletVersionEnum
    from tonsdk.utils import to_nano
except Exception as exc:  # pragma: no cover - dependency errors should fail fast
    raise RuntimeError("Failed to import tonsdk. Ensure dependency is installed.") from exc


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("ton_service")

PROVIDER_URL = os.getenv("TON_PROVIDER_URL", "https://toncenter.com/api/v2/")
NETWORK = os.getenv("NETWORK", "mainnet").lower()
INTERNAL_AUTH_TOKEN = os.getenv("INTERNAL_AUTH_TOKEN")
TON_WALLET_SEED = os.getenv("TON_WALLET_SEED")

if not INTERNAL_AUTH_TOKEN:
    logger.warning("INTERNAL_AUTH_TOKEN is not set. All requests will be rejected until provided.")

if not TON_WALLET_SEED:
    logger.error("TON_WALLET_SEED is required")
    sys.exit(1)

mnemonic_words = [word.strip() for word in TON_WALLET_SEED.split() if word.strip()]
wallet = Wallets.from_mnemonics(
    mnemonics=mnemonic_words,
    version=WalletVersionEnum.v4r2,
    workchain=0,
)

is_test_network = NETWORK != "mainnet"
wallet_address = wallet.address.to_string(
    is_user_friendly=True,
    is_bounceable=True,
    is_test_only=is_test_network,
)

app = FastAPI(title="TON Treasury Service", version="1.0.0")


class SendRequest(BaseModel):
    to_address: str = Field(..., description="Destination TON address")
    amount_ton: float = Field(..., gt=0, description="Amount in TON to transfer")
    comment: Optional[str] = Field(None, description="Optional comment payload")


class BalanceResponse(BaseModel):
    address: str
    balance_nano: int
    balance_ton: float
    network: str


class SendResponse(BaseModel):
    from_address: str
    to_address: str
    amount_ton: float
    boc: str
    network: str


def verify_internal_token(x_internal_token: Optional[str] = Header(None)) -> None:
    if not INTERNAL_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal token is not configured.",
        )

    if not x_internal_token or x_internal_token != INTERNAL_AUTH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


async def require_token(x_internal_token: Optional[str] = Header(None)) -> None:
    verify_internal_token(x_internal_token)


def _toncenter_get(method: str, params: dict) -> dict:
    url = f"{PROVIDER_URL.rstrip('/')}/{method}"
    response = requests.get(url, params=params, timeout=15)
    if response.status_code >= 400:
        logger.error("Toncenter GET %s failed: %s", method, response.text)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Toncenter GET failed")

    payload = response.json()
    if not payload.get("ok", False):
        logger.error("Toncenter GET %s error: %s", method, payload)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=payload.get("error", "Toncenter error"))

    return payload.get("result", {})


def _toncenter_post(method: str, data: dict) -> dict:
    url = f"{PROVIDER_URL.rstrip('/')}/{method}"
    response = requests.post(url, json=data, timeout=15)
    if response.status_code >= 400:
        logger.error("Toncenter POST %s failed: %s", method, response.text)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Toncenter POST failed")

    payload = response.json()
    if not payload.get("ok", False):
        logger.error("Toncenter POST %s error: %s", method, payload)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=payload.get("error", "Toncenter error"))

    return payload.get("result", {})


def _get_seqno() -> int:
    info = _toncenter_get("getWalletInformation", {"address": wallet_address})
    seqno = info.get("seqno")
    if seqno is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Missing seqno from Toncenter")
    return int(seqno)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "network": NETWORK, "address": wallet_address}


@app.get("/balance", response_model=BalanceResponse, dependencies=[Depends(require_token)])
async def get_balance() -> BalanceResponse:
    result = _toncenter_get("getAddressBalance", {"address": wallet_address})
    balance_nano = int(result)
    return BalanceResponse(
        address=wallet_address,
        balance_nano=balance_nano,
        balance_ton=balance_nano / 1_000_000_000,
        network=NETWORK,
    )


@app.post("/send", response_model=SendResponse, dependencies=[Depends(require_token)])
async def send_ton(request: SendRequest) -> SendResponse:
    seqno = _get_seqno()
    transfer = wallet.create_transfer_message(
        to_addr=request.to_address,
        amount=to_nano(request.amount_ton),
        seqno=seqno,
        payload=request.comment,
    )

    boc = transfer["message"].to_boc(False)
    boc_b64 = base64.b64encode(boc).decode()
    _toncenter_post("sendBoc", {"boc": boc_b64})

    return SendResponse(
        from_address=wallet_address,
        to_address=request.to_address,
        amount_ton=request.amount_ton,
        boc=boc_b64,
        network=NETWORK,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("service.main:app", host="0.0.0.0", port=7500, reload=False)
