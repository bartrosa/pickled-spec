"""Callee noise filtering: stdlib methods vs intra-project calls."""

from __future__ import annotations

from pathlib import Path


class Worker:
    def process(self) -> str:
        return "ok"


def strip_only() -> str:
    text = "hello"
    return text.strip()


def path_read(story_file: str) -> str:
    return Path(story_file).read_text(encoding="utf-8")


def use_worker() -> str:
    worker = Worker()
    return worker.process()
