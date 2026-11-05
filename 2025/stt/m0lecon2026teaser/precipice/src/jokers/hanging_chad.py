from .joker_base import JokerClass, JokerRarity


class HangingChad(JokerClass):
    description = "Retrigger first played card used in scoring 2 additional times"
    rarity = JokerRarity.COMMON
    price = 4

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if i == 0:
            # Retrigger 2 additional times
            for _ in range(2):
                state.message.append(f"{self.name}: retrigger card")
                if ignore_jokers is None:
                    ignore_jokers = set()
                ignore_jokers.add(self)
                state.compute_card_score(i, card, ignore_jokers=ignore_jokers)
                ignore_jokers.discard(self)
