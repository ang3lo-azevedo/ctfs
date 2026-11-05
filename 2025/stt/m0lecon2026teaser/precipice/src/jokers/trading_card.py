from .joker_base import JokerClass, JokerRarity


class TradingCard(JokerClass):
    description = "If first discard of round has only 1 card, destroy it"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def __init__(self):
        super().__init__()
        self.first_discard_of_round = False

    def on_discard(self, state):
        if self.first_discard_of_round and len(state.selected) == 1:
            card = state.selected.pop(0)
            state.hand.remove(card)
            for joker in state.jokers:
                joker.on_card_removed_from_deck(state, card)
        self.first_discard_of_round = False

    def on_round_start(self, state):
        self.first_discard_of_round = True

    def on_round_end(self, state):
        self.first_discard_of_round = False
