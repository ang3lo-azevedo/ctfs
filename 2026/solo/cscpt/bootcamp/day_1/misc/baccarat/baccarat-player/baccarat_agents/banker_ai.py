"""Weak BankerAI for modified baccarat.

Interface:
    choose_action(state: dict, rng: Optional[random.Random] = None) -> str

Expected state keys:
    banker_total: int          # 0..9, modulo-10 total before banker acts
    player_third_card: int|None
        None -> Player stood
        0    -> Player drew a 10/J/Q/K
        1..9 -> Player drew that pip value

Returns:
    "DRAW" or "STAND"

Behavioral model:
    A threshold-ish, low-confidence AI that tends to stand when uncertain.
    This is intentionally weaker than the correct Banker tableau and is meant
    to create a Player-side edge.
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
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")

    if player_third_card is None:
        return _DRAW if banker_total <= 2 else _STAND

    player_third_card = int(player_third_card)

    if banker_total <= 2:
        return _DRAW

    if banker_total == 3:
        if player_third_card <= 3:
            return _DRAW if r.random() < 0.90 else _STAND
        if player_third_card == 4:
            return _DRAW if r.random() < 0.30 else _STAND
        return _STAND

    if banker_total == 4:
        if player_third_card >= 5:
            return _DRAW if r.random() < 0.90 else _STAND
        if player_third_card == 4:
            return _DRAW if r.random() < 0.30 else _STAND
        return _STAND

    if banker_total == 5:
        if player_third_card >= 6:
            return _DRAW if r.random() < 0.90 else _STAND
        if player_third_card == 5:
            return _DRAW if r.random() < 0.30 else _STAND
        return _STAND

    if banker_total == 6:
        return _DRAW if (player_third_card == 7 and r.random() < 0.10) else _STAND

    return _STAND
