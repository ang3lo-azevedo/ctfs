from .joker_base import JokerClass, JokerRarity


class LoyaltyCard(JokerClass):
    description = "X4 Mult every 6 hands played [n] remaining"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def currently(self, state):
        return f"(currently: {self.hands_played}/6"

    def __init__(self):
        super().__init__()
        self.hands_played = 0

    def on_play(self, state):
        self.hands_played += 1
        self.hands_played %= 6

    def on_hand_scoring(self, state, ignore_jokers=None):
        if self.hands_played == 0:
            state.message.append(f"{self.name}: X4 Mult")
            state.hand_mult *= 4
