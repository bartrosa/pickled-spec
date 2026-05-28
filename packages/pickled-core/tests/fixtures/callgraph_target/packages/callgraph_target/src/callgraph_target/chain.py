"""Linear call chain for hop-depth tests."""


def step_two() -> str:
    return "two"


def step_one() -> str:
    return step_two() + "!"


def entry() -> str:
    return step_one()
