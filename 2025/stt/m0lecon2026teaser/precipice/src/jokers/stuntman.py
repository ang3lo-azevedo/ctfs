from .joker_base import JokerClass, JokerRarity


class Stuntman(JokerClass):
    description = "+250 Chips, -2 hand size"
    rarity = JokerRarity.RARE
    price = 7

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +250 Chips")
        state.hand_chips += 250

    def on_round_start(self, state):
        state.hand_size -= 2
