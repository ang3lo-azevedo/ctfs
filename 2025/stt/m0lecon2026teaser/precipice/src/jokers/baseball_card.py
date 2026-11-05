from .joker_base import JokerClass, JokerRarity


class BaseballCard(JokerClass):
    description = "Uncommon Jokers each give X1.5 Mult"
    rarity = JokerRarity.RARE
    price = 8

    def currently(self, state):
        mult = 1
        for joker in state.jokers:
            if joker.rarity == JokerRarity.UNCOMMON:
                mult *= 1.5
        return f"(currently: X{mult})"

    def on_hand_scoring(self, state, ignore_jokers=None):
        for joker in state.jokers:
            if joker.rarity == JokerRarity.UNCOMMON:
                state.message.append(
                    f"{self.name}: X1.5 Mult for Uncommon Joker")
                state.hand_mult *= 1.5
