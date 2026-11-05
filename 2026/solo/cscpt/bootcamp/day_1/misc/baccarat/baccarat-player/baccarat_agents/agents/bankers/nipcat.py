"""NipCat Banker agent.

This is the random-like Banker profile: vaguely sensible, but noisy and
inconsistent around the boundary.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _approximate_threshold(player_third_card: int | None) -> float:
    if player_third_card is None:
        return 4.5

    card = int(player_third_card)
    if card == 8:
        return 2.5
    if card == 0:
        return 3.0
    if card in (1, 2, 3):
        return 4.0
    if card in (4, 5):
        return 4.5
    if card in (6, 7):
        return 5.2
    return 3.4


def _draw_probability(banker_total: int, player_third_card: int | None) -> float:
    margin = _approximate_threshold(player_third_card) - banker_total

    if margin >= 2.0:
        probability = 0.94
    elif margin >= 1.0:
        probability = 0.76
    elif margin >= 0.0:
        probability = 0.56
    elif margin >= -1.0:
        probability = 0.26
    else:
        probability = 0.07

    if player_third_card in (6, 7):
        probability += 0.05
    if player_third_card is None:
        probability -= 0.04
    if player_third_card == 8:
        probability -= 0.05

    return max(0.02, min(0.98, probability))


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")

    probability = _draw_probability(banker_total, player_third_card)
    return _DRAW if r.random() < probability else _STAND
