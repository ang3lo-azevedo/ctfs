from .joker_base import JokerClass, JokerRarity


class FlowerPot(JokerClass):
    description = "X3 Mult if poker hand contains a Diamond card, Club card, Heart card, and Spade card"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_hand_scoring(self, state, ignore_jokers=None):
        if len(set(map(lambda c: c.suit, state.selected))) == 4:
            state.message.append(f"{self.name}: X3 Mult")
            state.hand_mult *= 3
