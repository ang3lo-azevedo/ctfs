from .joker_base import JokerClass, JokerRarity


class JokerStencil(JokerClass):
    description = "X1 Mult for each empty Joker slot. Joker Stencil included"
    rarity = JokerRarity.UNCOMMON
    price = 8

    def currently(self, state):
        empty_slots = state.max_joker_slots - \
            len(state.jokers) + \
            len(list(filter(lambda j: isinstance(j, type(self)), state.jokers)))
        if empty_slots > 0:
            return f"(currently: X{empty_slots})"
        return f"(currently: X1)"

    def on_hand_scoring(self, state, ignore_jokers=None):
        empty_slots = state.max_joker_slots - \
            len(state.jokers) + \
            len(list(filter(lambda j: isinstance(j, type(self)), state.jokers)))
        if empty_slots > 0:
            state.hand_mult *= empty_slots
