from .joker_base import JokerClass, JokerRarity


class Ramen(JokerClass):
    description = "X2 Mult, loses X0.01 Mult per card discarded"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        return f"(currently: X{self.ramen_mult})"

    def __init__(self):
        super().__init__()
        self.ramen_mult = 2

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: X{self.ramen_mult} Mult")
        state.hand_mult *= self.ramen_mult

    def on_discard(self, state):
        self.ramen_mult -= (0.01 * len(state.selected))
