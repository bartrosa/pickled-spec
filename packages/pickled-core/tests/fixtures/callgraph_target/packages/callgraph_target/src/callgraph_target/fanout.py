"""Many direct callees to exercise max_callees."""


def callee_a() -> int:
    return 1


def callee_b() -> int:
    return 2


def callee_c() -> int:
    return 3


def callee_d() -> int:
    return 4


def callee_e() -> int:
    return 5


def callee_f() -> int:
    return 6


def callee_g() -> int:
    return 7


def callee_h() -> int:
    return 8


def callee_i() -> int:
    return 9


def entry() -> int:
    return (
        callee_a()
        + callee_b()
        + callee_c()
        + callee_d()
        + callee_e()
        + callee_f()
        + callee_g()
        + callee_h()
        + callee_i()
    )
