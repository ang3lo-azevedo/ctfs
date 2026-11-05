from random import randint

from cards import CardClass

from .joker_base import JokerClass, JokerRarity


class AncientJoker(JokerClass):
    description = "Each played card with [suit] gives X1.5 Mult when scored, suit changes at end of round"
    rarity = JokerRarity.RARE
    price = 8

    def currently(self, state):
        return f"(currently: {CardClass.suit_art[self.target_suit]})"

    def __init__(self):
        super().__init__()
        self.on_round_end(None)

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.suit == self.target_suit:
            state.message.append(
                f"{self.name}: X1.5 Mult for {CardClass.suit_art[self.target_suit]} card")
            state.hand_mult *= 1.5

    def on_round_end(self, state):
        self.target_suit = randint(0, 3)
