from .joker_base import JokerClass, JokerRarity


class MysticSummit(JokerClass):
    description = "+15 Mult when 0 discards remaining"
    rarity = JokerRarity.COMMON
    price = 5

    def on_hand_scoring(self, state, ignore_jokers=None):
        if state.discards < 1:
            state.message.append(f"{self.name}: +15 Mult")
            state.hand_mult += 15
