from .joker_base import JokerClass, JokerRarity


class SquareJoker(JokerClass):
    description = "This Joker gains +4 Chips if played hand has exactly 4 cards"
    rarity = JokerRarity.COMMON
    price = 4

    def currently(self, state):
        return f"(currently: +{self.square_joker_chips})"

    def __init__(self):
        super().__init__()
        self.square_joker_chips = 0

    def on_play(self, state):
        if len(state.selected) == 4:
            self.square_joker_chips += 4

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{self.square_joker_chips} Chips")
        state.hand_chips += self.square_joker_chips
