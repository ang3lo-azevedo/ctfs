from random import choices

from .joker_base import JokerClass, JokerRarity


class RiffRaff(JokerClass):
    description = "When Blind is selected, create 2 Common Jokers (Must have room)"
    rarity = JokerRarity.COMMON
    price = 6

    def __init__(self):
        super().__init__()
        from jokers import jokers_map
        self.common_jokers = [joker_class for joker_class in jokers_map.values() if joker_class.rarity == JokerRarity.COMMON]

    def on_round_start(self, state):
        n = min(state.max_joker_slots - len(state.jokers), 2)
        if n == 0:
            return
        for new_joker_class in choices(self.common_jokers, k=n):
            state.jokers.append(new_joker_class())
