"""OmniCybr Player agent.

This is the classic ideal Player policy for baccarat-style third-card play.
"""

from __future__ import annotations

import random
from typing import Optional

_DRAW = "DRAW"
_STAND = "STAND"


def _rng(rng: Optional[random.Random]) -> random.Random:
    return rng if rng is not None else random


def choose_action(state: dict, rng: Optional[random.Random] = None) -> str:
    player_total = int(state["player_total"])
    return _DRAW if player_total <= 5 else _STAND
