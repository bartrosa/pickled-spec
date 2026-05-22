"""Candidate implementation: same behaviour as trivial_oracle for the demo."""

import sys


def main() -> None:
    raw = sys.stdin.read().strip()
    print(int(raw) * 2)


if __name__ == "__main__":
    main()
