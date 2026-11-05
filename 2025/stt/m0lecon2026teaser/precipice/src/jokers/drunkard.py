from .joker_base import JokerClass, JokerRarity


class Drunkard(JokerClass):
    description = "+1 discard each round"
    rarity = JokerRarity.COMMON
    price = 4

    def on_round_start(self, state):
        state.discards += 1
