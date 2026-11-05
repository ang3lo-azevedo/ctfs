from .joker_base import JokerClass, JokerRarity


class Burglar(JokerClass):
    description = "+3 Hands and lose all discards"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_round_start(self, state):
        state.hands += 3
        state.discards -= state.initial_discards
        print(state.discards, state.initial_discards)
