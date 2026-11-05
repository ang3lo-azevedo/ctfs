from .joker_base import JokerClass, JokerRarity


class SmileyFace(JokerClass):
    description = "Played face cards give +5 Mult when scored"
    rarity = JokerRarity.COMMON
    price = 4

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if state.is_face_card(card):
            state.message.append(f"{self.name}: +5 Mult for face card")
            state.hand_mult += 5
