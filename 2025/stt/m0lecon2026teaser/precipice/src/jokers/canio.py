from .joker_base import JokerClass, JokerRarity


class Canio(JokerClass):
    description = "This Joker gains X1 Mult when a face card is destroyed"
    rarity = JokerRarity.LEGENDARY
    price = 100

    def currently(self, state):
        return f"(currently: X{self.canio_mult})"

    def __init__(self):
        super().__init__()
        self.canio_mult = 1

    def on_card_removed_from_deck(self, state, card):
        if state.is_face_card(card):
            self.canio_mult += 1

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: X{self.canio_mult} Mult")
        state.hand_mult *= self.canio_mult
