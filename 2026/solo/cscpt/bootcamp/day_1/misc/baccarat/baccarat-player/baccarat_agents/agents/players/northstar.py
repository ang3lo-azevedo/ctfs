"""NorthStar Player agent.

This is the slightly-worse-than-ideal Player profile: almost ideal, with small
conservative leaks near the edge.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    player_total = int(state["player_total"])

    if player_total <= 3:
        return _DRAW
    if player_total == 4:
        return _DRAW if r.random() < 0.95 else _STAND
    if player_total == 5:
        return _DRAW if r.random() < 0.84 else _STAND
    if player_total == 6:
        return _DRAW if r.random() < 0.08 else _STAND
    return _STAND
