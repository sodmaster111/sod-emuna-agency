"""FastAPI middleware enforcing TON-based payments for premium endpoints."""
from __future__ import annotations

from typing import Iterable, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.plugins.ton_finance.wallet import TonWalletManager


class PaymentGatewayMiddleware(BaseHTTPMiddleware):
    """Return HTTP 402 responses when premium routes lack valid TON payments."""

    def __init__(
        self,
        app,
        wallet_manager: TonWalletManager,
        premium_endpoints: Iterable[str],
        expected_comment: str,
        minimum_amount: float = 0.0,
        payer_address: Optional[str] = None,
    ) -> None:
        super().__init__(app)
        self.wallet_manager = wallet_manager
        self.premium_endpoints = set(premium_endpoints)
        self.expected_comment = expected_comment
        self.minimum_amount = minimum_amount
        self.payer_address = payer_address

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.premium_endpoints:
            receipt = await self.wallet_manager.verify_transaction(
                expected_comment=self.expected_comment,
                minimum_amount=self.minimum_amount,
                payer_address=self.payer_address,
            )
            if not receipt:
                return JSONResponse(
                    status_code=402,
                    content={
                        "detail": "Payment required",
                        "wallet_address": self.wallet_manager.wallet.address.to_str(),
                        "expected_comment": self.expected_comment,
                        "minimum_amount_ton": self.minimum_amount,
                    },
                )

        response = await call_next(request)
        return response
