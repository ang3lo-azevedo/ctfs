import re
from enum import Enum

from cards import CardClass


class JokerRarity(Enum):
    COMMON = 0
    UNCOMMON = 1
    RARE = 2
    LEGENDARY = 3


JokerRarityChances = {
    JokerRarity.COMMON: 0.70,
    JokerRarity.UNCOMMON: 0.25,
    JokerRarity.RARE: 0.05,
    JokerRarity.LEGENDARY: 0.01,
}


class JokerClass(CardClass):
    description = ""
    rarity = JokerRarity.COMMON
    price = 0
    is_joker = True

    def currently(self, state):
        return ""

    @property
    def name(self):
        return re.sub(r"([A-Z])", r" \1", type(self).__name__).strip()

    @property
    def value(self):
        return self.price // 2

    def __init__(self):
        super().__init__(None, None)
        assert self.is_joker
        assert self.suit is None
        assert self.rank is None

    def on_joker_buy(self, state, joker):
        pass

    def on_joker_sell(self, state, joker):
        pass

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        pass

    def on_hand_scoring(self, state, ignore_jokers=None):
        pass

    def on_in_hand_card_scoring(self, state, i, card, ignore_jokers=None):
        pass

    def on_in_hand_scoring(self, state, ignore_jokers=None):
        pass

    def on_round_start(self, state):
        pass

    def on_round_end(self, state):
        pass

    def on_discard(self, state):
        pass

    def on_play(self, state):
        pass

    def on_hand_updated(self, state):
        pass

    def on_card_added_to_deck(self, state, card):
        pass

    def on_card_removed_from_deck(self, state, card):
        pass

    def overrides_is_face_card(self, state, card):
        return False
