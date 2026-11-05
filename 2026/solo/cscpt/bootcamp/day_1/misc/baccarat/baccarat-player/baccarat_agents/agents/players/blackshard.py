"""BlackShard Player agent.

This is the much-worse-than-ideal Player profile: a timid model that
overtrusts weak two-card totals and refuses many profitable draws.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _draw_probability(player_total: int) -> float:
    if player_total == 0:
        return 0.65
    if player_total == 1:
        return 0.28
    if player_total == 2:
        return 0.08
    if player_total == 3:
        return 0.02
    if player_total in (7, 8):
        return 0.08 if player_total == 7 else 0.02
    return 0.0


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    player_total = int(state["player_total"])
    probability = _draw_probability(player_total)
    return _DRAW if r.random() < probability else _STAND
