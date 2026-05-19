from __future__ import annotations

import logging
import sys

from pickled_core.mcp.stdio_logging import setup_logging_for_stdio


def test_logging_goes_to_stderr() -> None:
    setup_logging_for_stdio(level=logging.WARNING)
    root = logging.getLogger()
    assert root.handlers
    assert root.handlers[0].stream is sys.stderr
