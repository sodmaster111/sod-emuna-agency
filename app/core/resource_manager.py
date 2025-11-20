"""Resource guard monitoring memory and unloading idle assets."""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path
from typing import Callable, Iterable, List, Optional

import psutil

from app.core.kernel import PluginManager


class ResourceManager:
    """Background monitor that unloads idle agents or plugins under pressure."""

    def __init__(
        self,
        plugin_manager: Optional[PluginManager] = None,
        idle_agent_shutdown: Optional[Callable[[], Iterable[str]]] = None,
        threshold: float = 90.0,
        interval: float = 5.0,
    ) -> None:
        self.plugin_manager = plugin_manager or PluginManager()
        self.idle_agent_shutdown = idle_agent_shutdown
        self.threshold = threshold
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._db_path = Path("data/resource_guard.db")
        self._init_db()

    def start(self) -> None:
        if not self._thread.is_alive():
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=self.interval * 2)

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            mem_usage = psutil.virtual_memory().percent
            if mem_usage >= self.threshold:
                self._handle_pressure(mem_usage)
            time.sleep(self.interval)

    def _handle_pressure(self, mem_usage: float) -> None:
        actions: List[tuple[str, str, str]] = []

        if self.idle_agent_shutdown:
            for agent_name in self.idle_agent_shutdown():
                actions.append(("agent", agent_name, f"Memory usage at {mem_usage:.1f}%"))

        for plugin_name in list(self.plugin_manager.loaded_plugins.keys()):
            self.plugin_manager.unload_plugin(plugin_name)
            actions.append(("plugin", plugin_name, f"Memory usage at {mem_usage:.1f}%"))

        for target_type, target_name, reason in actions:
            self._log_action(target_type, target_name, reason)

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS kill_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_type TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _log_action(self, target_type: str, target_name: str, reason: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO kill_actions (target_type, target_name, reason) VALUES (?, ?, ?)",
                (target_type, target_name, reason),
            )
