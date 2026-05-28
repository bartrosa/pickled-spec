"""Mixed callee kinds: self, import, stdlib."""

from __future__ import annotations

import json

from callgraph_target import chain


class Worker:
    def helper(self) -> int:
        return 1

    def run(self) -> str:
        payload = json.dumps({"n": self.helper()})
        return payload + chain.entry()
