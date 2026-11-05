from .joker_base import JokerClass, JokerRarity


class Troubadour(JokerClass):
    description = "+2 hand size, -1 hand per round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def __init__(self):
        super().__init__()
        self.played_rounds = 0

    def on_round_start(self, state):
        self.played_rounds += 1
        state.hand_size += 2
        state.hands -= self.played_rounds
