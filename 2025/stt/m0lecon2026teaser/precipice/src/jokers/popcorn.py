from .joker_base import JokerClass, JokerRarity


class Popcorn(JokerClass):
    description = "+20 Mult -4 Mult per round played"
    rarity = JokerRarity.COMMON
    price = 5

    def currently(self, state):
        return f"(currently: +{20 - (4 * self.rounds_played)})"

    def __init__(self):
        super().__init__()
        self.rounds_played = 0

    def on_round_end(self, state):
        self.rounds_played += 1

    def on_hand_scoring(self, state, ignore_jokers=None):
        mult_gain = 20 - (4 * self.rounds_played)
        state.message.append(f"{self.name}: +{mult_gain} Mult")
        state.hand_mult += mult_gain
