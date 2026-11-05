from .joker_base import JokerClass, JokerRarity


class Baron(JokerClass):
    description = "Each King held in hand gives X1.5 Mult"
    rarity = JokerRarity.RARE
    price = 8

    def on_in_hand_card_scoring(self, state, i, card, ignore_jokers=None):
        # King has rank 13
        if card.rank == 13:
            state.message.append(f"{self.name}: X1.5 Mult for King")
            state.hand_mult *= 1.5
