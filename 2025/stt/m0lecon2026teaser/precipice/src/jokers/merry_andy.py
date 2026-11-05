from .joker_base import JokerClass, JokerRarity


class MerryAndy(JokerClass):
    description = "+3 discards each round, -1 hand size"
    rarity = JokerRarity.UNCOMMON
    price = 7

    def on_round_start(self, state):
        state.discards += 3
        state.hand_size -= 1
