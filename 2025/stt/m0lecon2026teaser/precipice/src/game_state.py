from functools import wraps
from math import prod
from random import choice, choices, shuffle
from sys import stderr

from numpy import float64

from cards import CardClass, CardEnhancement, cards, sort_hand
from jokers import JokerRarityChances, jokers_map
from rendering import render
from scoring import antes, base_scores, rank_chips


def renders(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        ret = method(self, *method_args, **method_kwargs)
        self.render()
        return ret
    return _impl


class GameState:
    antes = antes

    def __init__(self, initial_score=0, initial_hands=5, initial_discards=5, initial_hand_size=8, initial_reroll_price=5, initial_max_joker_slots=5) -> None:
        self.verbose_ui = False
        self.header = []
        self.message = []
        self.current_ante = 0
        self.game_over = False
        self.round_over = True
        # print(cards)
        self.initial_reroll_shop_price = initial_reroll_price
        self.reroll_shop_price = self.initial_reroll_shop_price
        self.game_deck = cards.copy()
        self.initial_deck_size = len(self.game_deck)
        self.discard_pile = []
        self.initial_hand_size = initial_hand_size
        self.hand_size = None
        self.drew = None
        self.hand = None
        self.selected = None
        self.suits_first_sorting = False
        self.initial_score = initial_score
        self.score = float64(self.initial_score)  # naneinf support
        self.initial_hands = initial_hands
        self.hands = None
        self.initial_discards = initial_discards
        self.discards = None
        self.initial_max_joker_slots = initial_max_joker_slots
        self.max_joker_slots = self.initial_max_joker_slots
        self.jokers = []
        self.jokers_selected = None
        self.jokers_selected_in_shop = None
        self.jokers_in_shop = None
        self.hand_type = None
        self.hand_chips = None
        self.hand_mult = None
        self.hand_levels = {ht: 1 for ht in base_scores.keys()}
        self.header += [
            "Welcome to precipice,",
            choice([
                "Facciam ballare sta fresca!",
                "It's not gambling if you know you're going to win!",
            ]),
            "Press ? for help.",
        ]

    def check_game_over(self):
        if self.score < self.antes[self.current_ante]:
            self.game_over = True
            self.header += [
                CardClass.joker_art,
                choice([
                    "Maybe Go Fish is more our speed...",
                    "We folded like a cheap suit!",
                    "Time for us to shuffle off and try again!",
                    "You know what they say, the house always wins!",
                    "Looks like we found out who the real Joker is!",
                    "Oh no, were you bluffing too?",
                    "Looks like the joke's on us!",
                    "If I had hands I would have covered my eyes!",
                    "I'm literally a fool, what's your excuse?",
                    "What a flop!",
                ]),
            ]
            self.message.append("Looks like you are fresh out of money.")

    def roll_shop(self):
        self.jokers_selected = []
        self.jokers_selected_in_shop = []
        self.jokers_in_shop = list(map(lambda j: j(), choices(
            list(set(jokers_map.values()) - set(self.jokers)),
            weights=list(
                map(lambda j: JokerRarityChances[j.rarity], jokers_map.values())),
            k=2
        )))

    @renders
    def in_shop(self):
        self.roll_shop()

    @renders
    def reroll_shop(self):
        if self.score < self.reroll_shop_price:
            self.message.append(f"You don't have enough money to re-roll the shop (${self.reroll_shop_price!r}).")
            return
        self.score -= 5
        self.roll_shop()
        self.check_game_over()

    def out_shop(self):
        self.jokers_selected = None
        self.jokers_selected_in_shop = None
        self.jokers_in_shop = None

    @renders
    def select_shop_joker(self, i):
        assert self.jokers_in_shop is not None
        assert self.jokers_selected_in_shop is not None
        s = None
        if not (0 <= i < len(self.jokers_in_shop)):
            self.message.append(f"You can't select joker {i+1!r}, shop has {len(self.jokers_in_shop)!r} jokers.")
            return
        s = self.jokers_in_shop[i]
        if s in set(self.jokers_selected_in_shop):
            self.jokers_selected_in_shop.remove(s)
        else:
            self.jokers_selected_in_shop.append(s)

    @renders
    def buy_jokers(self):
        assert self.jokers_in_shop is not None
        assert self.jokers_selected_in_shop is not None
        if len(self.jokers_selected_in_shop) > self.max_joker_slots - len(self.jokers):
            self.message.append(f"You can't have more than {self.max_joker_slots} jokers.")
            return
        price = 0
        for joker_class in self.jokers_selected_in_shop:
            price += joker_class.price
        if price > self.score:
            self.message.append(f"You don't have enough money to buy the selected jokers (${price!r}).")
            return
        while len(self.jokers_selected_in_shop) > 0:
            joker = self.jokers_selected_in_shop.pop(0)
            self.score -= joker.price
            self.jokers.append(joker)
            self.jokers_in_shop.remove(joker)
            for joker in self.jokers:
                joker.on_joker_buy(self, joker)
        self.check_game_over()

    @renders
    def select_joker(self, i):
        assert self.jokers_selected is not None
        s = None
        if not (0 <= i < len(self.jokers)):
            self.message.append(f"You can't select owned joker {i+1!r}, you own {len(self.jokers)!r} jokers.")
            return
        s = self.jokers[i]
        if s in set(self.jokers_selected):
            self.jokers_selected.remove(s)
        else:
            self.jokers_selected.append(s)

    @renders
    def sell_jokers(self):
        assert self.jokers_selected is not None
        while len(self.jokers_selected) > 0:
            joker = self.jokers_selected.pop(0)
            joker.on_joker_sell(self, joker)
            self.score += joker.value
            self.jokers.remove(joker)
            self.jokers_in_shop.append(joker)
            for joker in self.jokers:
                joker.on_joker_sell(self, joker)

    @renders
    def toggle_verbose_ui(self):
        self.verbose_ui = not self.verbose_ui

    @renders
    def buy_in(self):
        assert not self.game_over
        assert self.round_over
        self.header += [
            "Welcome to the game",
            choice([
                "90% of gamblers quit before they hit it big.",
                "Il 90% dei giocatori smette prima di vincere grosso.",
            ]),
            "Press ? for help.",
        ]
        if self.score == self.antes[self.current_ante]:
            self.message.append("Oof, this was a close one!")
            self.score = 0
        else:
            self.score -= self.antes[self.current_ante]
        if self.current_ante == len(self.antes) - 1:
            self.round_over = True
        # print(self.game_deck)
        # print(sort_hand(self.game_deck, reverse=False, suit_first=False))
        # print(sort_hand(self.game_deck, reverse=True, suit_first=True))
        self.hand_size = self.initial_hand_size
        self.hands = self.initial_hands
        self.discards = self.initial_discards
        self.selected = []
        # print(sort_hand(self.selected, suit_first=self.suits_first_sorting))
        self.hand_type = None
        self.hand_chips = None
        self.hand_mult = None
        self.round_over = False
        self.hand = []
        for joker in self.jokers:
            joker.on_round_start(self)
        shuffle(self.game_deck)
        # print(self.game_deck)
        # print(sort_hand(self.game_deck, reverse=False, suit_first=False))
        # print(sort_hand(self.game_deck, reverse=True, suit_first=True))
        self.consume()

    @renders
    def round_ended(self):
        assert not self.game_over
        assert self.round_over
        assert self.hand is not None
        if self.current_ante == len(self.antes) - 1:
            import os

            # import sys
            self.header += [
                CardClass.joker_art,
                choice([
                    "You Aced it!",
                    "You dealt with that pretty well!",
                    "Looks like you weren't bluffing!",
                    "Too bad these chips are all virtual...",
                    "How the turn tables.",
                    "Looks like I've taught you well!",
                    "You made some heads up plays!",
                    "Good thing I didn't bet against you!",
                ]),
            ]
            self.message.append("GG")
            with open("/flag", "r") as f:
                flag = f.read()
            self.message.append(flag)
            import sys
            print("FLAGGED", file=sys.stderr)
            print("ante:", self.current_ante, file=sys.stderr)
            print("score:", self.score, file=sys.stderr)
            print("deck_len:", len(self.game_deck), file=sys.stderr)
            list(map(lambda j: print(j.name, j.description, j.currently(self), file=sys.stderr), self.jokers))
            self.game_over = True
            return
        self.game_deck += self.hand
        self.game_deck += self.discard_pile
        self.discard_pile.clear()
        # print(self.game_deck)
        self.current_ante += 1
        self.hand = None
        self.selected = None
        self.hands = None
        self.discards = None
        self.hand_type = None
        self.hand_chips = None
        self.hand_mult = None
        self.header += [
            "Round over.",
        ]
        for joker in self.jokers:
            joker.on_round_end(self)
        self.check_game_over()

    @renders
    def toggle_sorting_order(self):
        self.suits_first_sorting = not self.suits_first_sorting
        self.hand = sort_hand(self.hand, suit_first=self.suits_first_sorting)

    def draw(self, n=1):
        return [self.game_deck.pop() for _ in range(n) if len(self.game_deck) > 0]

    def consume(self):
        if self.selected is None:
            return
        assert self.hand_size is not None
        assert self.hand is not None
        self.discard_pile += self.selected
        self.hand = list(set(self.hand) - set(self.selected))
        # print(self.hand)
        self.drew = self.draw(self.hand_size - len(self.hand))
        # print(self.drew)
        self.hand += self.drew
        # print(self.hand)
        self.hand = sort_hand(self.hand, suit_first=self.suits_first_sorting)
        # print(self.hand)
        self.selected = []
        for joker in self.jokers:
            joker.on_hand_updated(self)

    def compute_card_score(self, i, card, ignore_jokers=None):
        assert self.hand_chips is not None
        assert self.hand_mult is not None
        self.message.append(f"{card}: +{rank_chips[card.rank]} +{card.chips_bonus} Chips X{card.mult_bonus} Mult")
        # TODO STEEL for naneinf
        if card.enhancement == CardEnhancement.STONE:
            self.hand_chips += 50
        else:
            self.hand_chips += rank_chips[card.rank]
        self.hand_chips += card.chips_bonus
        self.hand_mult *= card.mult_bonus
        if ignore_jokers is None:
            ignore_jokers = set()
        for joker in self.jokers:
            if joker not in ignore_jokers:
                joker.on_card_scoring(
                    self, i, card, ignore_jokers=ignore_jokers)

    def compute_cards_score(self, ignore_jokers=None):
        if self.selected is None or len(self.selected) == 0:
            return
        assert self.hand_chips is not None
        assert self.hand_mult is not None
        for i, card in enumerate(self.selected):
            self.compute_card_score(i, card, ignore_jokers=ignore_jokers)

    def compute_hand_score(self, ignore_jokers=None):
        if self.selected is None or len(self.selected) == 0:
            return
        assert self.hand_chips is not None
        assert self.hand_mult is not None
        scores = {}
        if len(self.selected) > 0:
            scores["high_card"] = len(self.selected) > 0
        # print(self.selected)
        # print(sort_hand(self.selected, reverse=True, ace_after_king=True))
        # count cards per rank in played hand
        per_rank = {}
        for s in self.selected:
            if s.sorting_rank not in per_rank:
                per_rank[s.sorting_rank] = 1
            else:
                per_rank[s.sorting_rank] += 1
        # print(per_rank)
        # get the per rank card counts ordered from highest to lowest
        sorted_per_rank_values = sorted(per_rank.values(), reverse=True)
        # print(sorted_per_rank_values)
        # get the rank of each played card highest to lowest
        sorted_selected_ace_as_14 = [c.sorting_rank for c in sort_hand(
            self.selected, reverse=True, ace_after_king=True)]
        # print(sorted_selected_ace_as_14)
        sorted_selected_ace_as_01 = [c.rank for c in sort_hand(
            self.selected, reverse=True, ace_after_king=False)]
        # print(sorted_selected_ace_as_01)
        # count cards per suit in played hand
        per_suit = {}
        for s in self.selected:
            if s.suit not in per_suit:
                per_suit[s.suit] = 1
            else:
                per_suit[s.suit] += 1
        # print(per_suit)
        # get the per suit card counts ordered from highest to lowest
        sorted_per_suit_values = sorted(per_suit.values(), reverse=True)
        # print(sorted_per_suit_values)
        if len(self.selected) >= 2:
            scores["pair"] = len(
                sorted_per_rank_values) >= 1 and sorted_per_rank_values[0] >= 2
        if len(self.selected) >= 3:
            scores["three_of_a_kind"] = len(
                sorted_per_rank_values) >= 1 and sorted_per_rank_values[0] >= 3
        if len(self.selected) >= 4:
            scores["two_pair"] = len(
                sorted_per_rank_values) >= 2 and sorted_per_rank_values[0] >= 2 and sorted_per_rank_values[1] >= 2
            scores["four_of_a_kind"] = len(
                sorted_per_rank_values) >= 1 and sorted_per_rank_values[0] >= 4
        if len(self.selected) >= 5:
            # print(list(map(lambda ss: ss[0] - ss[1] == 1, zip(sorted_selected_ace_as_14[:-1], sorted_selected_ace_as_14[1:]))))
            # print(list(map(lambda ss: ss[0] - ss[1] == 1, zip(sorted_selected_ace_as_01[:-1], sorted_selected_ace_as_01[1:]))))
            scores["straight"] = (len(sorted_selected_ace_as_14) >= 2 and len(sorted_selected_ace_as_01) >= 2) and max([
                len(list(filter(bool, map(lambda ss: ss[0] - ss[1] == 1, zip(
                    # ace can be ither after k
                    sorted_selected_ace_as_14[:-1], sorted_selected_ace_as_14[1:]))))),
                len(list(filter(bool, map(lambda ss: ss[0] - ss[1] == 1, zip(
                    # or before 2
                    sorted_selected_ace_as_01[:-1], sorted_selected_ace_as_01[1:]))))),
            ]) >= 5 - 1  # diff of pairs has len -1
            scores["flush"] = len(
                sorted_per_suit_values) >= 1 and sorted_per_suit_values[0] >= 5
            scores["full_house"] = len(
                sorted_per_rank_values) >= 2 and sorted_per_rank_values[0] >= 3 and sorted_per_rank_values[1] >= 2
            scores["straight_flush"] = scores.get(
                "straight", False) and scores.get("flush", False)
            scores["royal_flush"] = scores.get("flush", False) and all(
                r in sorted_selected_ace_as_14 for r in range(10, 14+1))
            scores["five_of_a_kind"] = len(
                sorted_per_rank_values) >= 1 and sorted_per_rank_values[0] >= 5
            scores["flush_house"] = scores.get(
                "flush", False) and scores.get("full_house", False)
            scores["flush_five"] = scores.get(
                "flush", False) and scores.get("five_of_a_kind", False)
        # print(scores)
        # keys are reversed because later keys should have precedence (max of two equal values is the first seen)
        self.hand_type = max(reversed(
            scores.keys()), key=lambda h: 0 if not scores[h] else prod(base_scores[h]))
        # print(self.hand_type)
        if ignore_jokers is None:
            ignore_jokers = set()
        for joker in self.jokers:
            if joker not in ignore_jokers:
                joker.on_hand_scoring(self, ignore_jokers=ignore_jokers)
        self.hand_chips, self.hand_mult = [
            b * self.hand_levels[self.hand_type] for b in base_scores[self.hand_type]]

    def compute_in_hand_card_score(self, i, card, ignore_jokers=None):
        assert self.hand_chips is not None
        assert self.hand_mult is not None
        if card.enhancement == CardEnhancement.GOLD:
            self.hand_chips += 4
            self.message.append(f"{card}: +4 Chips")
        if ignore_jokers is None:
            ignore_jokers = set()
        for joker in self.jokers:
            if joker not in ignore_jokers:
                joker.on_in_hand_card_scoring(
                    self, i, card, ignore_jokers=ignore_jokers)

    def compute_in_hand_cards_score(self, ignore_jokers=None):
        assert self.hand is not None
        assert self.selected is not None
        assert self.hand_chips is not None
        assert self.hand_mult is not None
        if ignore_jokers is None:
            ignore_jokers = set()
        for i, card in enumerate(self.hand):
            if card not in self.selected:
                self.compute_in_hand_card_score(
                    i, card, ignore_jokers=ignore_jokers)
        for joker in self.jokers:
            if joker not in ignore_jokers:
                joker.on_in_hand_scoring(self, ignore_jokers=ignore_jokers)

    def compute_score(self):
        self.hand_chips, self.hand_mult = 0, 1
        # print("initial scoring:    ", self.hand_chips, self.hand_mult)
        try:  # fail safe on unimplemented jokers
            self.compute_hand_score()
            # print("hand_value scoring: ", self.hand_chips, self.hand_mult)
            self.compute_cards_score()
            # print("cards_value scoring:", self.hand_chips, self.hand_mult)
            self.compute_in_hand_cards_score()
            # print("in_hand_cards_value scoring:", self.hand_chips, self.hand_mult)
        except Exception as e:
            print(repr(e), file=stderr)

    @renders
    def select(self, i):
        assert self.hand is not None
        assert self.selected is not None
        s = None
        if not (0 <= i < len(self.hand)):
            self.message.append(f"You can't select card {i+1!r}, your hand has {len(self.hand)!r} cards.")
            return
        s = self.hand[i]
        if s in set(self.selected):
            self.selected.remove(s)
        elif len(self.selected) < 5:
            self.selected.append(s)
        else:
            self.message.append("You can't select more than 5 cards.")
        if len(self.selected) == 0:
            return
        self.compute_score()

    def _run_game_hand(self, is_play=True):
        assert self.hand is not None
        assert self.selected is not None
        assert self.hands is not None
        assert self.discards is not None
        assert len(set(self.hand) - set(self.selected)
                   ) == len(self.hand) - len(self.selected)
        if len(self.selected) == 0:
            return
        self.compute_score()
        if is_play:
            assert self.hand_type is not None and self.hand_chips is not None and self.hand_mult is not None
            self.score += self.hand_chips * self.hand_mult
            self.hands -= 1
            for joker in self.jokers:
                joker.on_play(self)
        else:
            if self.discards == 0:
                self.message.append("No more discards to play.")
                return
            self.discards -= 1
            for joker in self.jokers:
                joker.on_discard(self)
            self.hand_type = None
            self.hand_chips = None
            self.hand_mult = None
        self.consume()
        if is_play and self.hands == 0:
            self.message.append("No more hands to play.")
            self.round_over = True
            return
        if len(self.hand) == 0:
            self.message.append("No more cards to play.")
            self.round_over = True
            return

    @renders
    def play(self):
        self._run_game_hand(is_play=True)

    @renders
    def discard(self):
        self._run_game_hand(is_play=False)

    def render(self):
        if not self.round_over:
            render(
                hand=self.hand,
                drew=self.drew,
                selected=self.selected,
                header=self.header,
                message=self.message,
                score=self.score,
                hands_discards=[self.hands, self.discards],
                ante=self.current_ante,
                next_stake=self.antes[self.current_ante +
                                      1] if self.current_ante < len(self.antes) - 2 else None,
                hand_scoring=[
                    self.hand_type,
                    self.hand_chips,
                    self.hand_mult,
                ] if self.hand_type is not None else None,
                jokers=self.jokers,
                state=self,
                verbose=self.verbose_ui,
            )
            self.drew = None
        elif not self.game_over:
            render(
                header=self.header,
                message=self.message,
                score=self.score,
                ante=self.current_ante,
                next_stake=self.antes[self.current_ante],
                jokers=self.jokers,
                jokers_selected=self.jokers_selected,
                jokers_in_shop=self.jokers_in_shop,
                jokers_selected_in_shop=self.jokers_selected_in_shop,
                state=self,
                verbose=self.verbose_ui,
            )
        else:
            render(
                header=self.header,
                message=self.message,
                score=self.score,
                ante=self.current_ante,
                next_stake=self.antes[self.current_ante],
                verbose=self.verbose_ui,
            )
        self.header.clear()
        self.message.clear()
        self.hand_type = None
        self.hand_chips = None
        self.hand_mult = None

    @renders
    def quit(self):
        self.game_over = True
        self.message.append("Quitter. Chi non risica non rosica.")

    def upgrade_hand_level(self, hand_type):
        self.hand_levels[hand_type] += 1
        hand_chips, hand_mult = [b * self.hand_levels[hand_type]
                                 for b in base_scores[hand_type]]
        self.message.append(f"{hand_type} level upgraded to {self.hand_levels[hand_type]}: ${hand_chips} X{hand_mult}")

    def is_face_card(self, card):
        for joker in self.jokers:
            if joker.overrides_is_face_card(self, card):
                return True
        return card.is_face_card()
