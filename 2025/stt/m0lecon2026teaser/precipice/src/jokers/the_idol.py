from random import randint

from cards import CardClass

from .joker_base import JokerClass, JokerRarity


class TheIdol(JokerClass):
    description = "Each played [rank] of [suit] gives X2 Mult when scored Card changes every round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        return f"(currently: {CardClass.art_factory(self.target_rank, self.target_suit)})"

    def __init__(self):
        super().__init__()
        self.on_round_end(None)

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.rank == self.target_rank and card.suit == self.target_suit:
            state.message.append(
                f"{self.name}: X2 Mult for {CardClass.art_factory(self.target_rank, self.target_suit)} card")
            state.hand_mult *= 2

    def on_round_end(self, state):
        self.target_rank = randint(1, 13)
        self.target_suit = randint(0, 3)
