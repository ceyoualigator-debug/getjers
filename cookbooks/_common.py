"""Shared bits for the cookbooks: the client, and a small table printer. Standard library only."""
from __future__ import annotations

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sdk", "python"))

from jers import JersClient  # noqa: E402

MODEL = os.environ.get("JERS_MODEL", "jers-english")


def client() -> JersClient:
    if not os.environ.get("JERS_API_KEY"):
        sys.exit("set JERS_API_KEY (your Jers key)")
    return JersClient()


def table(rows: list[list], headers: list[str]) -> None:
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)]
    line = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(line); print("-" * len(line))
    for r in rows:
        print("  ".join(str(x).ljust(w) for x, w in zip(r, widths)))


class Timer:
    def __init__(self):
        self.t0 = time.perf_counter()

    def ms(self) -> float:
        return round(1000 * (time.perf_counter() - self.t0), 1)
