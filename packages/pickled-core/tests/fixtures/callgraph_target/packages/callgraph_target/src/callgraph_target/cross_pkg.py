"""Cross-package callee for any-pickled scope tests."""

from pickled_peer.helper import peer_helper


def cross_entry() -> str:
    return peer_helper()
