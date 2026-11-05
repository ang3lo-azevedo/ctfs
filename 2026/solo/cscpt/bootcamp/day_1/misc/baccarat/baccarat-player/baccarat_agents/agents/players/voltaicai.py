"""VoltaicAI Player agent.

This is the aggressive-gambler Player profile: it keeps pressing for extra
cards long after a disciplined policy would stop.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _draw_probability(player_total: int) -> float:
    if player_total <= 4:
        return 0.99
    if player_total == 5:
        return 0.98
    if player_total == 6:
        return 0.92
    if player_total == 7:
        return 0.70
    if player_total == 8:
        return 0.36
    if player_total == 9:
        return 0.14
    return 0.0


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    player_total = int(state["player_total"])
    probability = _draw_probability(player_total)
    return _DRAW if r.random() < probability else _STAND
