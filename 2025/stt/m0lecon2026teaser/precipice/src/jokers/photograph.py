from .joker_base import JokerClass, JokerRarity


class Photograph(JokerClass):
    description = "First played face card gives X2 Mult when scored"
    rarity = JokerRarity.COMMON
    price = 5

    def __init__(self):
        super().__init__()
        self.is_first_face = False

    def on_hand_scoring(self, state, ignore_jokers=None):
        self.is_first_face = True

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if state.is_face_card(card):
            state.message.append(f"{self.name}: X2 Mult for first face card")
            state.hand_mult *= 2
            self.is_first_face = False

    def on_play(self, state):
        self.is_first_face = False
