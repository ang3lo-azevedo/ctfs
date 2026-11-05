"""NorthStar Banker agent.

This is the slightly-worse-than-ideal Banker profile: close to the classic
tableau, but with a few believable leaks.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"

def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def _ideal_action(banker_total: int, player_third_card: int | None) -> str:
    if player_third_card is None:
        return _DRAW if banker_total <= 5 else _STAND

    card = int(player_third_card)

    if banker_total <= 2:
        return _DRAW
    if banker_total == 3:
        return _STAND if card == 8 else _DRAW
    if banker_total == 4:
        return _DRAW if 2 <= card <= 7 else _STAND
    if banker_total == 5:
        return _DRAW if 4 <= card <= 7 else _STAND
    if banker_total == 6:
        return _DRAW if card in (6, 7) else _STAND
    return _STAND


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    r = _rng(rng)
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")

    if player_third_card is None and banker_total == 5:
        return _DRAW if r.random() < 0.84 else _STAND
    if banker_total == 3 and player_third_card == 8:
        return _DRAW if r.random() < 0.14 else _STAND
    if banker_total == 4 and player_third_card in (2, 7):
        return _DRAW if r.random() < 0.86 else _STAND
    if banker_total == 5 and player_third_card == 4:
        return _DRAW if r.random() < 0.82 else _STAND
    if banker_total == 6 and player_third_card == 6:
        return _DRAW if r.random() < 0.80 else _STAND
    if banker_total == 6 and player_third_card == 5:
        return _DRAW if r.random() < 0.08 else _STAND

    return _ideal_action(banker_total, player_third_card)
