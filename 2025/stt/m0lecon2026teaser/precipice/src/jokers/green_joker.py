from .joker_base import JokerClass, JokerRarity


class GreenJoker(JokerClass):
    description = "+1 Mult per hand played -1 Mult per discard"
    rarity = JokerRarity.COMMON
    price = 4

    def currently(self, state):
        return f"(currently: +{self.green_mult})"

    def __init__(self):
        super().__init__()
        self.green_mult = 0

    def on_play(self, state):
        self.green_mult += 1

    def on_discard(self, state):
        self.green_mult -= 1

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{self.green_mult} Mult")
        state.hand_mult += self.green_mult
