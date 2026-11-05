from .joker_base import JokerClass, JokerRarity


class Mime(JokerClass):
    description = "Retrigger all card held in hand abilities"
    rarity = JokerRarity.UNCOMMON
    price = 5

    def on_in_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: retrigger hand cards")
        if ignore_jokers is None:
            ignore_jokers = set()
        ignore_jokers.add(self)
        state.compute_in_hand_cards_score(ignore_jokers=ignore_jokers)
        ignore_jokers.discard(self)
