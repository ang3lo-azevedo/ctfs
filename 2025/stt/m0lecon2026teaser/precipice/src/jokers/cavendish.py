from random import randint

from .joker_base import JokerClass, JokerRarity


class Cavendish(JokerClass):
    description = "X3 Mult 1 in 1000 chance this card is destroyed at the end of round"
    rarity = JokerRarity.COMMON
    price = 4

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: X3 Mult")
        state.hand_mult *= 3

    def on_round_end(self, state):
        if randint(1, 1000) == 1:
            if self in state.jokers:
                state.jokers.remove(self)
