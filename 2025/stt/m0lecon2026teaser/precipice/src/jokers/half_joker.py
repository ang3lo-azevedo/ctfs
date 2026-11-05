from .joker_base import JokerClass, JokerRarity


class HalfJoker(JokerClass):
    description = "+20 Mult if played hand contains 3 or fewer cards"
    rarity = JokerRarity.COMMON
    price = 5

    def on_hand_scoring(self, state, ignore_jokers=None):
        if len(state.selected) <= 3:
            state.message.append(f"{self.name}: +20 Mult")
            state.hand_mult += 20
