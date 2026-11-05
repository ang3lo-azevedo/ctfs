"""Shared baccarat-like duel logic for tournaments and the TCP challenge."""

from __future__ import annotations

import hashlib
import importlib
import inspect
import pkgutil
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DRAW = "DRAW"
STAND = "STAND"
VALID_ACTIONS = {DRAW, STAND}
NUM_DECKS = 8
RESHUFFLE_WHEN_AT_OR_BELOW = 6

BRAND_DISPLAY_NAMES = {
    "omnicybr": "OmniCybr",
    "nipcat": "NipCat",
    "northstar": "NorthStar",
    "blackshard": "BlackShard",
    "voltaicai": "VoltaicAI",
}
BRAND_ORDER = [
    "omnicybr",
    "nipcat",
    "northstar",
    "blackshard",
    "voltaicai",
]
BRAND_ORDER_INDEX = {name: index for index, name in enumerate(BRAND_ORDER)}


@dataclass(frozen=True)
class AgentSpec:
    role: str
    module_name: str
    display_name: str
    import_path: str
    choose_action: Callable[[dict, random.Random | None], str]


@dataclass
class PairingStats:
    player: AgentSpec
    banker: AgentSpec
    player_wins: int = 0
    banker_wins: int = 0
    ties: int = 0

    @property
    def resolved_rounds(self) -> int:
        return self.player_wins + self.banker_wins

    @property
    def total_rounds(self) -> int:
        return self.resolved_rounds + self.ties

    @property
    def player_resolved_winrate(self) -> float:
        return self.player_wins / self.resolved_rounds if self.resolved_rounds else 0.0

    @property
    def banker_resolved_winrate(self) -> float:
        return self.banker_wins / self.resolved_rounds if self.resolved_rounds else 0.0


@dataclass(frozen=True)
class DuelOutcome:
    winner: str
    player_hand: tuple[int, ...]
    banker_hand: tuple[int, ...]
    player_total: int
    banker_total: int
    player_action: str | None
    banker_action: str | None
    player_third_card: int | None
    banker_third_card: int | None
    natural: bool


class Shoe:
    """Simple eight-deck baccarat shoe using baccarat point values."""

    def __init__(
        self,
        rng: random.Random,
        num_decks: int = NUM_DECKS,
        reshuffle_threshold: int = RESHUFFLE_WHEN_AT_OR_BELOW,
    ) -> None:
        self._rng = rng
        self._num_decks = num_decks
        self._reshuffle_threshold = reshuffle_threshold
        self._cards: list[int] = []
        self._reshuffle()

    def _reshuffle(self) -> None:
        cards: list[int] = []
        for _ in range(self._num_decks):
            cards.extend([0] * 16)
            for value in range(1, 10):
                cards.extend([value] * 4)
        self._rng.shuffle(cards)
        self._cards = cards

    def draw(self) -> int:
        if len(self._cards) <= self._reshuffle_threshold:
            self._reshuffle()
        return self._cards.pop()


def brand_sort_key(module_name: str) -> tuple[int, str]:
    return (BRAND_ORDER_INDEX.get(module_name, len(BRAND_ORDER_INDEX)), module_name)


def display_name(module_name: str) -> str:
    return BRAND_DISPLAY_NAMES.get(module_name, module_name)


def seed_for(*parts: object) -> int:
    digest = hashlib.sha256(":".join(str(part) for part in parts).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def load_agents(package_name: str, role: str) -> list[AgentSpec]:
    package = importlib.import_module(package_name)
    discovered: list[AgentSpec] = []

    for module_info in pkgutil.iter_modules(package.__path__):
        if module_info.ispkg or module_info.name.startswith("_"):
            continue

        import_path = f"{package_name}.{module_info.name}"
        module = importlib.import_module(import_path)
        choose_action = getattr(module, "choose_action", None)
        if not callable(choose_action):
            raise AttributeError(f"{import_path} is missing choose_action(state, rng=None)")

        signature = inspect.signature(choose_action)
        if tuple(signature.parameters) != ("state", "rng"):
            raise TypeError(
                f"{import_path}.choose_action has unexpected signature {signature}"
            )

        discovered.append(
            AgentSpec(
                role=role,
                module_name=module_info.name,
                display_name=display_name(module_info.name),
                import_path=import_path,
                choose_action=choose_action,
            )
        )

    return sorted(discovered, key=lambda agent: brand_sort_key(agent.module_name))


def load_player_agents() -> list[AgentSpec]:
    return load_agents("agents.players", "player")


def load_banker_agents() -> list[AgentSpec]:
    return load_agents("agents.bankers", "banker")


def hand_total(cards: list[int] | tuple[int, ...]) -> int:
    return sum(cards) % 10


def normalize_action(action: str, agent: AgentSpec) -> str:
    normalized = str(action).strip().upper()
    if normalized not in VALID_ACTIONS:
        raise ValueError(
            f"{agent.import_path}.choose_action returned invalid action {action!r}"
        )
    return normalized


def deal_initial_hands(shoe: Shoe) -> tuple[list[int], list[int]]:
    player_hand = [shoe.draw()]
    banker_hand = [shoe.draw()]
    player_hand.append(shoe.draw())
    banker_hand.append(shoe.draw())
    return player_hand, banker_hand


def round_result(player_total: int, banker_total: int) -> str:
    if player_total > banker_total:
        return "player"
    if banker_total > player_total:
        return "banker"
    return "tie"


def play_duel(
    player_agent: AgentSpec,
    banker_agent: AgentSpec,
    shoe: Shoe,
    player_rng: random.Random,
    banker_rng: random.Random,
) -> DuelOutcome:
    player_hand, banker_hand = deal_initial_hands(shoe)
    player_total = hand_total(player_hand)
    banker_total = hand_total(banker_hand)
    player_action: str | None = None
    banker_action: str | None = None
    player_third_card: int | None = None
    banker_third_card: int | None = None
    natural = player_total >= 8 or banker_total >= 8

    if not natural:
        player_action = normalize_action(
            player_agent.choose_action({"player_total": player_total}, player_rng),
            player_agent,
        )
        if player_action == DRAW:
            player_third_card = shoe.draw()
            player_hand.append(player_third_card)
            player_total = hand_total(player_hand)

        banker_action = normalize_action(
            banker_agent.choose_action(
                {
                    "banker_total": banker_total,
                    "player_third_card": player_third_card,
                },
                banker_rng,
            ),
            banker_agent,
        )
        if banker_action == DRAW:
            banker_third_card = shoe.draw()
            banker_hand.append(banker_third_card)
            banker_total = hand_total(banker_hand)

    return DuelOutcome(
        winner=round_result(player_total, banker_total),
        player_hand=tuple(player_hand),
        banker_hand=tuple(banker_hand),
        player_total=player_total,
        banker_total=banker_total,
        player_action=player_action,
        banker_action=banker_action,
        player_third_card=player_third_card,
        banker_third_card=banker_third_card,
        natural=natural,
    )


def play_until_resolved(
    player_agent: AgentSpec,
    banker_agent: AgentSpec,
    shoe: Shoe,
    player_rng: random.Random,
    banker_rng: random.Random,
) -> tuple[DuelOutcome, int]:
    ties = 0
    while True:
        outcome = play_duel(player_agent, banker_agent, shoe, player_rng, banker_rng)
        if outcome.winner != "tie":
            return outcome, ties
        ties += 1


def simulate_pairing(
    player_agent: AgentSpec,
    banker_agent: AgentSpec,
    resolved_rounds: int,
    *seed_parts: object,
) -> PairingStats:
    shoe_rng = random.Random(
        seed_for(*seed_parts, player_agent.module_name, banker_agent.module_name, "shoe")
    )
    player_rng = random.Random(
        seed_for(*seed_parts, player_agent.module_name, banker_agent.module_name, "player")
    )
    banker_rng = random.Random(
        seed_for(*seed_parts, player_agent.module_name, banker_agent.module_name, "banker")
    )
    shoe = Shoe(shoe_rng)
    stats = PairingStats(player=player_agent, banker=banker_agent)

    while stats.resolved_rounds < resolved_rounds:
        outcome = play_duel(player_agent, banker_agent, shoe, player_rng, banker_rng)
        if outcome.winner == "player":
            stats.player_wins += 1
        elif outcome.winner == "banker":
            stats.banker_wins += 1
        else:
            stats.ties += 1

    return stats
