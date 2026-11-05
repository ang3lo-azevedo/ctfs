from random import randint

from cards import CardClass

from .joker_base import JokerClass, JokerRarity


class Certificate(JokerClass):
    description = "When round begins, add a random playing card to your hand"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_round_start(self, state):
        new_card = CardClass(randint(0, 3), randint(1, 13))
        state.hand.append(new_card)
        for joker in state.jokers:
            joker.on_card_added_to_deck(state, new_card)
