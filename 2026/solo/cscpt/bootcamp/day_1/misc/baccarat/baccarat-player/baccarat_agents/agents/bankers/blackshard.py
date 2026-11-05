"""BlackShard Banker agent.

This is the much-worse-than-ideal Banker profile: a timid model that stands on
many totals where the Banker should keep fighting for a better hand.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _draw_probability(banker_total: int, player_third_card: int | None) -> float:
    probability_by_total = {
        0: 0.65,
        1: 0.28,
        2: 0.08,
        3: 0.02,
        4: 0.00,
        5: 0.00,
        6: 0.00,
        7: 0.08,
        8: 0.02,
        9: 0.00,
    }
    probability = probability_by_total.get(banker_total, 0.0)

    if player_third_card in (8, 9):
        probability += 0.02
    if player_third_card in (6, 7):
        probability -= 0.02

    return max(0.0, min(0.70, probability))


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")
    probability = _draw_probability(banker_total, player_third_card)
    return _DRAW if r.random() < probability else _STAND
