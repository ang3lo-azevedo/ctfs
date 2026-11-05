from .joker_base import JokerClass, JokerRarity


class BlueJoker(JokerClass):
    description = "+2 Chips for each remaining card in deck"
    rarity = JokerRarity.COMMON
    price = 5

    def currently(self, state):
        return f"(currently: +{2 * len(state.game_deck)})"

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{2 * len(state.game_deck)} Chips")
        state.hand_chips += 2 * len(state.game_deck)
