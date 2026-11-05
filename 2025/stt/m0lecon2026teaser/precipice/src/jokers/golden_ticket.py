from cards import CardEnhancement

from .joker_base import JokerClass, JokerRarity


class GoldenTicket(JokerClass):
    description = "Gold cards give +12 mult when scored"
    rarity = JokerRarity.COMMON
    price = 5

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.enhancement == CardEnhancement.GOLD:
            state.message.append(f"{self.name}: +12 Mult for Gold card")
            card.hand_mult += 12
