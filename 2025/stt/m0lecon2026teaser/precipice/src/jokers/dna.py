import copy

from .joker_base import JokerClass, JokerRarity


class DNA(JokerClass):
    description = "If first hand of round has only 1 card, add a permanent copy to deck and draw it to hand"
    rarity = JokerRarity.RARE
    price = 8

    def __init__(self):
        super().__init__()
        self.first_play_of_round = False

    def on_play(self, state):
        # Check if it's the first hand of the round and has only 1 card
        if self.first_play_of_round and len(state.selected) == 1:
            new_card = copy.deepcopy(state.selected[0])
            state.game_deck.append(new_card)
            for joker in state.jokers:
                joker.on_card_added_to_deck(state, new_card)
        self.first_play_of_round = False

    def on_round_start(self, state):
        self.first_play_of_round = True

    def on_round_end(self, state):
        self.first_play_of_round = False
