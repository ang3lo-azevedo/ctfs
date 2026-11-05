from random import randint

from .joker_base import JokerClass, JokerRarity


class GrosMichel(JokerClass):
    description = "+15 Mult 1 in 6 chance this is destroyed at the end of round."
    rarity = JokerRarity.COMMON
    price = 5

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +15 Mult")
        state.hand_mult += 15

    def on_round_end(self, state):
        if randint(1, 6) == 1:
            if self in state.jokers:
                state.jokers.remove(self)
