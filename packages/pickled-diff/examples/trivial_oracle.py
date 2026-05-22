"""Reference implementation: double the integer read from stdin."""

import sys


def main() -> None:
    raw = sys.stdin.read().strip()
    print(int(raw) * 2)


if __name__ == "__main__":
    main()
