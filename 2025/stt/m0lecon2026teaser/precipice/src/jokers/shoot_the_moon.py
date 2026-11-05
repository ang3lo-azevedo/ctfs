from .joker_base import JokerClass, JokerRarity


class ShootTheMoon(JokerClass):
    description = "Each Queen held in hand gives +13 Mult"
    rarity = JokerRarity.COMMON
    price = 5

    def on_in_hand_card_scoring(self, state, i, card, ignore_jokers=None):
        # Queen has rank 12
        if card.rank == 12:
            state.message.append(f"{self.name}: +13 Mult for Queen")
            state.hand_mult += 13
