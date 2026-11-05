from .joker_base import JokerClass, JokerRarity


class Pareidolia(JokerClass):
    description = "All cards are considered face cards"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def overrides_is_face_card(self, state, card):
        return True
