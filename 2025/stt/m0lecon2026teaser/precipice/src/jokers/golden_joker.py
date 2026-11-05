from cards import CardEnhancement

from .joker_base import JokerClass, JokerRarity


class GoldenJoker(JokerClass):
    description = "+12 Mult for each Gold card held in hand"
    rarity = JokerRarity.COMMON
    price = 6

    def on_in_hand_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.enhancement == CardEnhancement.GOLD:
            state.message.append(f"{self.name}: +12 Mult for Gold card")
            state.hand_mult += 12
