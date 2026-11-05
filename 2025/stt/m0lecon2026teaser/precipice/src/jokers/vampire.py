from cards import CardEnhancement

from .joker_base import JokerClass, JokerRarity


class Vampire(JokerClass):
    description = "This Joker gains X0.1 Mult per scoring Enhanced card played, removes card Enhancement"
    rarity = JokerRarity.UNCOMMON
    price = 7

    def currently(self, state):
        return f"(currently: X{self.vampire_mult})"

    def __init__(self):
        super().__init__()
        self.vampire_mult = 1

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.enhancement != CardEnhancement.NONE:
            self.vampire_mult += 0.1
            card.enhancement = CardEnhancement.NONE

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: X{self.vampire_mult} Mult")
        state.hand_mult *= self.vampire_mult
