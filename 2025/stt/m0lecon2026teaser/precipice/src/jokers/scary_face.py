from .joker_base import JokerClass, JokerRarity


class ScaryFace(JokerClass):
    description = "Played face cards give +30 Chips when scored"
    rarity = JokerRarity.COMMON
    price = 4

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if state.is_face_card(card):
            state.message.append(f"{self.name}: +30 Chips for face card")
            state.hand_chips += 30
