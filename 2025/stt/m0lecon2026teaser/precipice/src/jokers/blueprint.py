from copy import deepcopy

from .joker_base import JokerClass, JokerRarity


class Blueprint(JokerClass):
    description = "Copies ability of Joker to the right"
    rarity = JokerRarity.RARE
    price = 10

    def currently(self, state):
        if self.copied_joker is None:
            return "(none)"
        return f"(currently: {self.copied_joker.name})"

    def __init__(self):
        super().__init__()
        self.copied_joker = None

    def find_joker_to_copy(self, state):
        self.copied_joker = None
        found = False
        for joker in state.jokers:
            if found:
                self.copied_joker = deepcopy(joker)
                break
            if joker is self:
                found = True
                continue

    def on_joker_buy(self, state, joker):
        self.find_joker_to_copy(state)
        if self.copied_joker is not None:
            self.copied_joker.on_joker_buy(state, joker)

    def on_joker_sell(self, state, joker):
        self.find_joker_to_copy(state)
        if self.copied_joker is not None:
            self.copied_joker.on_joker_sell(state, joker)

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if self.copied_joker is not None:
            self.copied_joker.on_card_scoring(
                state, i, card, ignore_jokers=ignore_jokers)

    def on_hand_scoring(self, state, ignore_jokers=None):
        if self.copied_joker is not None:
            self.copied_joker.on_hand_scoring(
                state, ignore_jokers=ignore_jokers)

    def on_in_hand_card_scoring(self, state, i, card, ignore_jokers=None):
        if self.copied_joker is not None:
            self.copied_joker.on_in_hand_card_scoring(
                state, i, card, ignore_jokers=ignore_jokers)

    def on_in_hand_scoring(self, state, ignore_jokers=None):
        if self.copied_joker is not None:
            self.copied_joker.on_in_hand_scoring(
                state, ignore_jokers=ignore_jokers)

    def on_round_start(self, state):
        if self.copied_joker is not None:
            self.copied_joker.on_round_start(state)

    def on_round_end(self, state):
        if self.copied_joker is not None:
            self.copied_joker.on_round_end(state)

    def on_discard(self, state):
        if self.copied_joker is not None:
            self.copied_joker.on_discard(state)

    def on_play(self, state):
        if self.copied_joker is not None:
            self.copied_joker.on_play(state)

    def on_hand_updated(self, state):
        if self.copied_joker is not None:
            self.copied_joker.on_hand_updated(state)

    def on_card_added_to_deck(self, state, card):
        if self.copied_joker is not None:
            self.copied_joker.on_card_added_to_deck(state, card)

    def on_card_removed_from_deck(self, state, card):
        if self.copied_joker is not None:
            self.copied_joker.on_card_removed_from_deck(state, card)

    def overrides_is_face_card(self, state, card):
        if self.copied_joker is not None:
            return self.copied_joker.overrides_is_face_card(state, card)
        return super().overrides_is_face_card(state, card)
