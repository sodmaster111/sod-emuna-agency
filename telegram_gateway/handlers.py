from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Optional

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from telegram_gateway.backend_client import BackendClient

router = Router()


def _format_logs(logs: List[Dict[str, Any]]) -> str:
    if not logs:
        return "No log entries available."

    lines = []
    for entry in logs:
        agent = entry.get("agent") or entry.get("agent_name") or "unknown"
        thought = entry.get("thought") or entry.get("action") or entry.get("message")
        timestamp = entry.get("timestamp") or entry.get("created_at")
        snippet = textwrap.shorten(str(thought or ""), width=160, placeholder="…")
        if timestamp:
            lines.append(f"[{timestamp}] {agent}: {snippet}")
        else:
            lines.append(f"{agent}: {snippet}")

    return "\n".join(lines)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer(
        "Welcome to the SOD Telegram gateway!\n"
        "Use /schedule <task> to delegate work, /status <task_id> to check progress, "
        "or /logs to read recent Pinkas entries."
    )


@router.message(Command("schedule"))
async def handle_schedule(message: Message, backend_client: BackendClient) -> None:
    if not message.text:
        await message.answer("Please provide a task description after /schedule.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Please provide a task description after /schedule.")
        return

    task_description = parts[1].strip()
    if not task_description:
        await message.answer("Please provide a task description after /schedule.")
        return

    user = message.from_user
    user_id = user.id if user else 0
    username = user.username if user else None

    try:
        result = await backend_client.schedule_task(
            task=task_description,
            user_id=user_id,
            username=username,
        )
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Failed to schedule task: {exc}")
        return

    task_id: Optional[str] = None
    if isinstance(result, dict):
        task_id = result.get("task_id") or result.get("id")

    if task_id:
        await message.answer(f"Task scheduled! Your task id is: {task_id}")
    else:
        await message.answer("Task scheduled, but no task id was returned by the backend.")


@router.message(Command("status"))
async def handle_status(message: Message, backend_client: BackendClient) -> None:
    if not message.text:
        await message.answer("Usage: /status <task_id>")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /status <task_id>")
        return

    task_id = parts[1].strip()
    if not task_id:
        await message.answer("Usage: /status <task_id>")
        return

    try:
        result = await backend_client.get_status(task_id)
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Failed to fetch status: {exc}")
        return

    status = result.get("status") if isinstance(result, dict) else None
    if status:
        await message.answer(f"Status for {task_id}: {status}\nDetails: {result}")
    else:
        await message.answer(f"Status for {task_id}: {result}")


@router.message(Command("logs"))
async def handle_logs(message: Message, backend_client: BackendClient) -> None:
    limit = 5
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 2:
            try:
                limit = max(1, min(int(parts[1]), 20))
            except ValueError:
                await message.answer("Invalid limit. Please provide a number, e.g. /logs 5")
                return

    try:
        logs = await backend_client.fetch_logs(limit=limit)
    except Exception as exc:  # noqa: BLE001
        await message.answer(f"Failed to fetch logs: {exc}")
        return

    await message.answer(_format_logs(logs))


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "Commands:\n"
        "/schedule <task> - schedule a new task with the backend\n"
        "/status <task_id> - check the status of a task\n"
        "/logs [limit] - view recent Pinkas log entries\n"
        "/help - show this help message"
    )
