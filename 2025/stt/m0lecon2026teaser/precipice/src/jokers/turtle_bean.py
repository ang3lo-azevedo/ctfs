from .joker_base import JokerClass, JokerRarity


class TurtleBean(JokerClass):
    description = "+5 hand size, reduces by 1 each round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        return f"(currently: {self.hand_size_bonus})"

    def __init__(self):
        super().__init__()
        self.hand_size_bonus = 5

    def on_round_start(self, state):
        state.hand_size += self.hand_size_bonus

    def on_round_end(self, state):
        self.hand_size_bonus -= 1
