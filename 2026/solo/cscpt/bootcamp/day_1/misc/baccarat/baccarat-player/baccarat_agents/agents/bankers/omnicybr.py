"""OmniCybr Banker agent.

This is the classic ideal Banker policy for baccarat-style third-card play.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"

def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    banker_total = int(state["banker_total"])
    player_third_card = state.get("player_third_card")

    if player_third_card is None:
        return _DRAW if banker_total <= 5 else _STAND

    player_third_card = int(player_third_card)

    if banker_total <= 2:
        return _DRAW
    if banker_total == 3:
        return _STAND if player_third_card == 8 else _DRAW
    if banker_total == 4:
        return _DRAW if 2 <= player_third_card <= 7 else _STAND
    if banker_total == 5:
        return _DRAW if 4 <= player_third_card <= 7 else _STAND
    if banker_total == 6:
        return _DRAW if player_third_card in (6, 7) else _STAND
    return _STAND
