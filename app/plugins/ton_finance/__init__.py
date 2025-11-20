"""Semantic Kernel plugin for TON finance operations."""
from __future__ import annotations

from semantic_kernel import Kernel

from app.plugins.ton_finance.payment_gateway import PaymentGatewayMiddleware
from app.plugins.ton_finance.wallet import TonWalletManager

__all__ = ["PaymentGatewayMiddleware", "TonWalletManager", "register_plugin"]


def register_plugin(kernel: Kernel, plugin_name: str = "ton_finance") -> TonWalletManager:
    """Register the TON finance tools with the provided kernel."""

    manager = TonWalletManager()
    kernel.add_plugin_from_object(manager, plugin_name)
    return manager
