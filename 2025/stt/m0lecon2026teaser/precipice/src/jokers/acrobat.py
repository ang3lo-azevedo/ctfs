from .joker_base import JokerClass, JokerRarity


class Acrobat(JokerClass):
    description = "X3 Mult on final hand of round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_hand_scoring(self, state, ignore_jokers=None):
        # Check if it's the final hand of the round
        if state.hands < 1:
            state.message.append(f"{self.name}: X3 Mult")
            state.hand_mult *= 3
