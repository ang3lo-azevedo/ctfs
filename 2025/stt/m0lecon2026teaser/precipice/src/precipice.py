#!/usr/bin/env python3

from numpy import float32

from game_state import GameState
from scoring import base_scores


def play_round(state):
    assert not state.round_over
    last_cmd = ""
    try:
        while not state.round_over:
            ts = input(">")
            if len(ts) == 0:
                ts = last_cmd
            for t in ts.split(" "):
                if len(t) == 0:
                    continue
                elif t in {"?", "h", "help", }:
                    print(
                        " \"?\" or \"h\" or \"help\" to show this message",
                        " \"v\" or \"verbose\" to toggle verbose ui",
                        " \"s\" or \"sort\" to toggle sorting by rank or by suit",
                        " <a number> to select card by number",
                        " \"p\" or \"play\" to play hand",
                        " \"d\" or \"discard\" to discard hand",
                        " \"a\" or \"ability\" to see the jokers abilities",
                        " \"l\" or \"level\" to see hand level and scoring",
                        sep="\n"
                    )
                elif t in {"v", "verbose", }:
                    state.toggle_verbose_ui()
                elif t in {"s", "sort", }:
                    state.toggle_sorting_order()
                elif t in {"p", "play", }:
                    state.play()
                elif t in {"d", "discard", }:
                    state.discard()
                elif t.isdecimal():
                    state.select(int(t)-1)
                elif t in {"a", "ability", }:
                    for i, j in enumerate(state.jokers, start=1):
                        print(
                            f" -{i}: {j.name}: {j.description} {j.currently(state)}")
                elif t in {"l", "level", }:
                    for hand_type in base_scores.keys():
                        hand_level = state.hand_levels[hand_type]
                        chips, mult = [
                            b * hand_level for b in base_scores[hand_type]]
                        print(f" {hand_type}: {hand_level}: ${chips} X{mult}")
                else:
                    print(f"command not supported: {t!r}")
            last_cmd = ts
    except KeyboardInterrupt:
        pass


def play_game(state):
    state.in_shop()
    last_cmd = ""
    try:
        while not state.game_over:
            t = input(">").strip()
            if len(t) == 0:
                t = last_cmd
            if t in {"?", "h", "help", }:
                print(
                    " \"?\" or \"h\" or \"help\" to show this message",
                    " \"v\" or \"verbose\" to toggle verbose ui",
                    " \"p\" or \"play\" to buy in and play the next ante",
                    " \"f\" or \"forfit\" to forfit (Loser)",
                    f" \"r\" or \"reroll\" to reroll the shop (${state.reroll_shop_price})",
                    " <a number> to select shop joker by number",
                    " \"b\" or \"buy\" to buy select jokers",
                    " -<a number> to select owned joker by number",
                    " \"s\" or \"sell\" to sell select jokers",
                    sep="\n"
                )
            elif t in {"v", "verbose", }:
                state.toggle_verbose_ui()
            elif t in {"p", "play", }:
                state.out_shop()
                state.buy_in()
                play_round(state)
                state.round_ended()
                state.in_shop()
            elif t in {"f", "forfit", }:
                state.quit()
                break
            elif t in {"r", "reroll", }:
                state.reroll_shop()
            elif t.isdecimal():
                state.select_shop_joker(int(t)-1)
            elif t[0] == "-" and t[1:].isdecimal():
                state.select_joker(int(t[1:])-1)
            elif t in {"b", "buy", }:
                state.buy_jokers()
            elif t in {"s", "sell", }:
                state.sell_jokers()
            else:
                print(f"command not supported: {t!r}")
            last_cmd = t
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    state = GameState(
        initial_score=0,
        initial_hands=5,
        initial_discards=5,
    )
    play_game(state)
