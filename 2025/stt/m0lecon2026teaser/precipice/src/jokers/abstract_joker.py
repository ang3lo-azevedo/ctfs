from .joker_base import JokerClass, JokerRarity


class AbstractJoker(JokerClass):
    description = "+3 Mult for each Joker card"
    rarity = JokerRarity.COMMON
    price = 4

    def currently(self, state):
        return f"(currently: +{3 * len(state.jokers)})"

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{3 * len(state.jokers)} Mult")
        state.hand_mult += 3 * len(state.jokers)
