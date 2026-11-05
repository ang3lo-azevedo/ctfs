from .joker_base import JokerClass, JokerRarity


class Hiker(JokerClass):
    description = "Every played card permanently gains +5 Chips when scored"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def on_play(self, state):
        for card in state.selected:
            card.chips_bonus += 5
