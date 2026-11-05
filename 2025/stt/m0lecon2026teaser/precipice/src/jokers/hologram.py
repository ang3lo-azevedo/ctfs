from .joker_base import JokerClass, JokerRarity


class Hologram(JokerClass):
    description = "This Joker gains X0.25 Mult every time a playing card is added to your deck"
    rarity = JokerRarity.UNCOMMON
    price = 7

    def currently(self, state):
        return f"(currently: X{self.hologram_mult})"

    def __init__(self):
        super().__init__()
        self.hologram_mult = 1

    def on_card_added_to_deck(self, state, card):
        self.hologram_mult += 0.25

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: X{self.hologram_mult} Mult")
        state.hand_mult *= self.hologram_mult
