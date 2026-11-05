from .joker_base import JokerClass, JokerRarity


class Dusk(JokerClass):
    description = "Retrigger all played cards in final hand of the round"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def on_hand_scoring(self, state, ignore_jokers=None):
        if state.hands < 1:  # Final hand of the round
            state.message.append(f"{self.name}: retrigger cards")
            if ignore_jokers is None:
                ignore_jokers = set()
            ignore_jokers.add(self)
            state.compute_cards_score(ignore_jokers=ignore_jokers)
            ignore_jokers.discard(self)
