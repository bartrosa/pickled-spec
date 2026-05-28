"""Deliberate mutual recursion for cycle tests."""


def pong() -> None:
    ping()


def ping() -> None:
    pong()
