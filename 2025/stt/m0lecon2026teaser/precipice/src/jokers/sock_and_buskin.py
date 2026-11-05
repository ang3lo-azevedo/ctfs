from .joker_base import JokerClass, JokerRarity


class SockAndBuskin(JokerClass):
    description = "Retrigger all played face cards"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def on_card_scoring(self, state, i, card, ignore_jokers=None):
        if state.is_face_card(card):
            state.message.append(f"{self.name}: retrigger card")
            if ignore_jokers is None:
                ignore_jokers = set()
            ignore_jokers.add(self)
            state.compute_card_score(i, card, ignore_jokers=ignore_jokers)
            ignore_jokers.discard(self)
