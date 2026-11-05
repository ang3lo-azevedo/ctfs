"""Reproducible smoke test for the branded baccarat duel agents."""

from __future__ import annotations

import importlib
import inspect
import random

MODULE_CASES = [
    (
        "Banker",
        "OmniCybr",
        "agents.bankers.omnicybr",
        [
            {"banker_total": 2, "player_third_card": None},
            {"banker_total": 6, "player_third_card": None},
            {"banker_total": 4, "player_third_card": 8},
            {"banker_total": 5, "player_third_card": 6},
        ],
    ),
    (
        "Banker",
        "NipCat",
        "agents.bankers.nipcat",
        [
            {"banker_total": 3, "player_third_card": 0},
            {"banker_total": 4, "player_third_card": 4},
            {"banker_total": 6, "player_third_card": 7},
        ],
    ),
    (
        "Banker",
        "NorthStar",
        "agents.bankers.northstar",
        [
            {"banker_total": 6, "player_third_card": None},
            {"banker_total": 2, "player_third_card": 8},
            {"banker_total": 7, "player_third_card": 6},
        ],
    ),
    (
        "Banker",
        "BlackShard",
        "agents.bankers.blackshard",
        [
            {"banker_total": 3, "player_third_card": None},
            {"banker_total": 4, "player_third_card": 7},
            {"banker_total": 6, "player_third_card": 9},
        ],
    ),
    (
        "Banker",
        "VoltaicAI",
        "agents.bankers.voltaicai",
        [
            {"banker_total": 6, "player_third_card": None},
            {"banker_total": 7, "player_third_card": 6},
            {"banker_total": 5, "player_third_card": 8},
        ],
    ),
    (
        "Player",
        "OmniCybr",
        "agents.players.omnicybr",
        [
            {"player_total": 4},
            {"player_total": 5},
            {"player_total": 6},
        ],
    ),
    (
        "Player",
        "NipCat",
        "agents.players.nipcat",
        [
            {"player_total": 4},
            {"player_total": 6},
            {"player_total": 8},
        ],
    ),
    (
        "Player",
        "NorthStar",
        "agents.players.northstar",
        [
            {"player_total": 4},
            {"player_total": 5},
            {"player_total": 6},
        ],
    ),
    (
        "Player",
        "BlackShard",
        "agents.players.blackshard",
        [
            {"player_total": 3},
            {"player_total": 5},
            {"player_total": 7},
        ],
    ),
    (
        "Player",
        "VoltaicAI",
        "agents.players.voltaicai",
        [
            {"player_total": 5},
            {"player_total": 6},
            {"player_total": 8},
        ],
    ),
]

VALID_ACTIONS = {"DRAW", "STAND"}


def main() -> None:
    for role, brand, module_name, cases in MODULE_CASES:
        module = importlib.import_module(module_name)
        if not hasattr(module, "choose_action"):
            raise AssertionError(f"{module_name} is missing choose_action")

        action_fn = module.choose_action
        signature = inspect.signature(action_fn)
        if tuple(signature.parameters) != ("state", "rng"):
            raise AssertionError(
                f"{module_name}.choose_action has unexpected signature {signature}"
            )

        print(f"[{role} | {brand} | {module_name}]")
        for index, state in enumerate(cases):
            rng = random.Random(1000 + (37 * len(module_name)) + index)
            action = action_fn(state, rng)
            if action not in VALID_ACTIONS:
                raise AssertionError(
                    f"{module_name}.choose_action returned invalid action {action!r}"
                )
            print(f"  case {index + 1}: state={state} -> {action}")
        print()


if __name__ == "__main__":
    main()
