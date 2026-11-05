from .joker_base import JokerClass, JokerRarity


class Joker(JokerClass):
    description = "+4 Mult"
    rarity = JokerRarity.COMMON
    price = 2

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +4 Mult")
        state.hand_mult += 4
