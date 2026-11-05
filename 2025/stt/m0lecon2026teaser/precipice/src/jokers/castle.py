from random import randint

from cards import CardClass

from .joker_base import JokerClass, JokerRarity


class Castle(JokerClass):
    description = "This Joker gains +3 Chips per discarded [suit] card, suit changes every round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        return f"(currently: {CardClass.suit_art[self.target_suit]}), +{self.gained_chips})"

    def __init__(self):
        super().__init__()
        self.on_round_end(None)
        self.gained_chips = 0

    def on_discard(self, state):
        for card in state.selected:
            if card.suit == self.target_suit:
                self.gained_chips += 3

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{self.gained_chips} Chips")
        state.hand_chips += self.gained_chips

    def on_round_end(self, state):
        self.target_suit = randint(0, 3)  # Change suit every round
