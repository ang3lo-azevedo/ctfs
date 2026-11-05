from cards import CardEnhancement

from .joker_base import JokerClass, JokerRarity


class StoneJoker(JokerClass):
    description = "+25 Chips for each Stone card in your deck"
    rarity = JokerRarity.UNCOMMON
    price = 6

    def currently(self, state):
        chips = 0
        for card in state.game_deck:
            if card.enhancement == CardEnhancement.STONE:
                chips += 25
        return f"(currently: +{chips})"

    def on_hand_scoring(self, state, ignore_jokers=None):
        for card in state.game_deck:
            if card.enhancement == CardEnhancement.STONE:
                state.message.append(f"{self.name}: +25 Chips for Stone card")
                state.hand_chips += 25
