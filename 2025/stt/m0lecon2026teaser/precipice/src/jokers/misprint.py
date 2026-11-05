from random import randint

from .joker_base import JokerClass, JokerRarity


class Misprint(JokerClass):
    description = "+0-23 Mult"
    rarity = JokerRarity.COMMON
    price = 4

    def on_hand_scoring(self, state, ignore_jokers=None):
        mult_gain = randint(0, 23)
        state.message.append(f"{self.name}: +{mult_gain} Mult")
        state.hand_mult += mult_gain
