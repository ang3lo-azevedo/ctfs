from .joker_base import JokerClass, JokerRarity


class Banner(JokerClass):
    description = "+30 Chips for each remaining discard"
    rarity = JokerRarity.COMMON
    price = 5

    def currently(self, state):
        if state.discards is not None:
            return f"(currently: +{30 * state.discards})"
        return ""

    def on_hand_scoring(self, state, ignore_jokers=None):
        state.message.append(f"{self.name}: +{30 * state.discards} Chips")
        state.hand_chips += 30 * state.discards
