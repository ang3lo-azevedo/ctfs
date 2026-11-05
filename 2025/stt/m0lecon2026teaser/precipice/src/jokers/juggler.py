from .joker_base import JokerClass, JokerRarity


class Juggler(JokerClass):
    description = "+1 hand size"
    rarity = JokerRarity.COMMON
    price = 4

    def on_round_start(self, state):
        state.hand_size += 1
