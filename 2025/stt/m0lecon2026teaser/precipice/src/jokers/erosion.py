from .joker_base import JokerClass, JokerRarity


class Erosion(JokerClass):
    description = "+4 Mult for each card below [the deck's starting size] in your full deck"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        if self.hand is None:
            return ""
        cards_below_initial = state.initial_deck_size - \
            (len(state.game_deck) + len(state.hand) + len(state.discard_pile))
        return f"(currently: +{4 * cards_below_initial})"

    def on_hand_scoring(self, state, ignore_jokers=None):
        cards_below_initial = state.initial_deck_size - \
            (len(state.game_deck) + len(state.hand) + len(state.discard_pile))
        state.message.append(f"{self.name}: +{4 * cards_below_initial} Mult")
        state.hand_mult += 4 * cards_below_initial
