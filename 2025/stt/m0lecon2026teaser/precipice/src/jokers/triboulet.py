from .joker_base import JokerClass, JokerRarity


class Triboulet(JokerClass):
    description = "Played Kings and Queens each give X2 Mult when scored"
    rarity = JokerRarity.LEGENDARY
    price = 100

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if card.rank == 12 or card.rank == 13:  # Queen or King
            state.message.append(f"{self.name}: X2 Mult for King/Queen")
            state.hand_mult *= 2
