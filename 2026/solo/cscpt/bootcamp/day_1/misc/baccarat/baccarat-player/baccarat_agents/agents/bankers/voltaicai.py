"""VoltaicAI Banker agent.

This is the aggressive-gambler Banker profile: a high-variance overdrawer that
keeps reaching for one more card.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _aggressive_threshold(player_third_card: int | None) -> float:
    if player_third_card is None:
        return 7.6

    card = int(player_third_card)
    if card == 8:
        return 6.7
    if card == 0:
        return 7.0
    if card in (1, 2, 3):
        return 7.4
    if card in (4, 5, 9):
        return 7.7
    return 8.1


def _draw_probability(banker_total: int, player_third_card: int | None) -> float:
    margin = _aggressive_threshold(player_third_card) - banker_total

    if margin >= 1.5:
        probability = 0.99
    elif margin >= 0.5:
        probability = 0.94
    elif margin >= 0.0:
        probability = 0.78
    elif margin >= -1.0:
        probability = 0.46
    elif margin >= -2.0:
        probability = 0.18
    else:
        probability = 0.08

    return max(0.03, min(0.99, probability))


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")

    probability = _draw_probability(banker_total, player_third_card)
    return _DRAW if r.random() < probability else _STAND
