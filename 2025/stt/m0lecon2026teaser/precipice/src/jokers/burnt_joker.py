from .joker_base import JokerClass, JokerRarity


class BurntJoker(JokerClass):
    description = "Upgrade the level of the first discarded poker hand each round"
    rarity = JokerRarity.RARE
    price = 8

    def __init__(self):
        super().__init__()
        self.first_discard_of_round = False

    def on_discard(self, state):
        if self.first_discard_of_round:
            state.upgrade_hand_level(state.hand_type)
        self.first_discard_of_round = False

    def on_round_start(self, state):
        self.first_discard_of_round = True

    def on_round_end(self, state):
        self.first_discard_of_round = False
