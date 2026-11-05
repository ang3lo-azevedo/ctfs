"""NipCat Player agent.

This is the random-like Player profile: weak, noisy, and fuzzy around the
right threshold.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"

_DRAW_PROBABILITY_BY_TOTAL = {
    0: 0.99,
    1: 0.95,
    2: 0.88,
    3: 0.77,
    4: 0.63,
    5: 0.46,
    6: 0.22,
    7: 0.08,
    8: 0.02,
    9: 0.01,
}


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    player_total = int(state["player_total"])
    probability = _DRAW_PROBABILITY_BY_TOTAL.get(player_total, 0.0)
    return _DRAW if r.random() < probability else _STAND
