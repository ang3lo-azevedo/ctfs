from random import randint

from .joker_base import JokerClass, JokerRarity


class SpaceJoker(JokerClass):
    description = "1 in 4 chance to upgrade level of played poker hand"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def on_hand_scoring(self, state, ignore_jokers=None):
        if randint(1, 4) == 1:
            if state.hand_type is not None:
                state.upgrade_hand_level(state.hand_type)
