from random import randint

from cards import CardClass, CardEnhancement

from .joker_base import JokerClass, JokerRarity


class MarbleJoker(JokerClass):
    description = "Adds one Stone card to your deck at the start of each round"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_round_start(self, state):
        new_card = CardClass(randint(0, 3), randint(
            1, 13), enhancement=CardEnhancement.STONE)
        state.game_deck.append(new_card)
        for joker in state.jokers:
            joker.on_card_added_to_deck(state, new_card)
