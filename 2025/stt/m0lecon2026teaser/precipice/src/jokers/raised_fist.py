from .joker_base import JokerClass, JokerRarity


class RaisedFist(JokerClass):
    description = "Adds double the rank of lowest ranked card held in hand to Mult"
    rarity = JokerRarity.COMMON
    price = 5

    def currently(self, state):
        if state.hand is None or state.selected is None:
            return ""
        ranks_in_hand = [
            card.rank for card in state.hand if card not in state.selected]
        if len(ranks_in_hand) > 0:
            state.hand_mult += 2 * min(ranks_in_hand)
            return f"(currently: X{2 * min(ranks_in_hand)})"
        return f"(currently: X1)"

    def on_hand_scoring(self, state, ignore_jokers=None):
        ranks_in_hand = [
            card.rank for card in state.hand if card not in state.selected]
        if len(ranks_in_hand) > 0:
            mult_gain = 2 * min(ranks_in_hand)
            state.message.append(f"{self.name}: +{mult_gain} Mult")
            state.hand_mult += mult_gain
