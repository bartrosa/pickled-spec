#!/usr/bin/env python3
"""Smoke test the umbrella MCP server over stdio.

Subprocess-spawns ``uv run pickled-spec mcp --transport stdio``, sends a
tools/list JSON-RPC request, asserts at least two tools come back (bdd_*,
rules_*), exits 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "--directory",
            str(REPO_ROOT),
            "--extra",
            "mcp",
            "pickled-spec",
            "mcp",
            "--transport",
            "stdio",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(REPO_ROOT),
        text=True,
    )
    stderr_chunks: list[str] = []

    def _drain_stderr() -> None:
        if proc.stderr is None:
            return
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            stderr_chunks.append(line)

    threading.Thread(target=_drain_stderr, daemon=True).start()
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "smoke", "version": "0"},
        },
    }
    initialized = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    }
    listed = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    assert proc.stdin is not None
    assert proc.stdout is not None
    proc.stdin.write(json.dumps(init) + "\n")
    proc.stdin.flush()
    stdout_parts: list[str] = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        stdout_parts.append(line)
        msg = json.loads(line)
        if msg.get("id") == 1:
            break
    proc.stdin.write(json.dumps(initialized) + "\n")
    proc.stdin.write(json.dumps(listed) + "\n")
    proc.stdin.flush()
    time.sleep(2.0)
    proc.stdin.close()
    chunk = proc.stdout.read(65536)
    if chunk:
        stdout_parts.append(chunk)
    proc.terminate()
    proc.wait(timeout=5)
    stderr = "".join(stderr_chunks)
    stdout = "".join(stdout_parts)
    if stderr:
        print(stderr, file=sys.stderr, end="")
    if proc.returncode not in (0, None) and proc.returncode != 0:
        print(f"server exited {proc.returncode}", file=sys.stderr)
        return proc.returncode or 1
    tool_names: list[str] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("id") == 2 and "result" in msg:
            tools = msg["result"].get("tools", [])
            tool_names = [t.get("name", "") for t in tools]
            break
    if len(tool_names) < 2:
        print(f"expected >=2 tools, got {tool_names!r}", file=sys.stderr)
        print("stdout:", stdout[:2000], file=sys.stderr)
        return 1
    print(f"ok: {len(tool_names)} tools: {', '.join(tool_names[:8])}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
