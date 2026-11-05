from cards import CardEnhancement

from .joker_base import JokerClass, JokerRarity


class MidasMask(JokerClass):
    description = "All face cards become Gold cards when played"
    rarity = JokerRarity.UNCOMMON
    price = 7

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if state.is_face_card(card):
            card.enhancement = CardEnhancement.GOLD
