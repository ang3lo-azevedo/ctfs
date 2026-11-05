from enum import Enum
from itertools import chain

cards_mode = "txt"
cards_mode = "utf"


class CardEnhancement(Enum):
    NONE = 0
    GOLD = 1
    STONE = 2
    STEEL = 3


# ANSI escape codes for colors
COLORS = {
    "reset": "\033[0m",
    "black": "\033[90m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "white_background": "\033[107m",
}

SUIT_COLORS = {
    None: COLORS["reset"],
    0: COLORS["red"],
    1: COLORS["purple"],
    2: COLORS["blue"],
    3: COLORS["black"],
}


class Card:
    suits = None
    figures = None
    ranks = None
    ranks_sorting_map = {r: i for i, r in enumerate(
        chain(range(2, 13+1), range(1, 1+1)),
        start=2
    )} | {None: 0}
    is_joker = False

    @classmethod
    def clean_art(cls, art):
        # Remove all ANSI color codes for rank/suit extraction
        for color in COLORS.values():
            art = art.replace(color, "")
        return art

    @classmethod
    def color_art(cls, art, suit=None, rank=None, enhancement=CardEnhancement.NONE):
        if enhancement == CardEnhancement.GOLD:
            return f"{COLORS['yellow']}{art}{COLORS['reset']}"
        elif enhancement == CardEnhancement.STONE:
            return f"{COLORS['white_background']}{COLORS['black']}{art}🪨{COLORS['reset']}"
        assert enhancement == CardEnhancement.NONE
        return f"{SUIT_COLORS[suit]}{art}{COLORS['reset']}"

    @classmethod
    def art_factory(cls, suit, rank, enhancement=CardEnhancement.NONE):
        raise NotImplementedError()

    @classmethod
    def rank_from_art(cls, art):
        raise NotImplementedError()

    @classmethod
    def suit_from_art(cls, art):
        raise NotImplementedError()

    def __init__(self, suit, rank, chips_bonus=0, mult_bonus=1, enhancement=CardEnhancement.NONE):
        self.rank = rank
        self.sorting_rank = self.ranks_sorting_map[self.rank]
        self.suit = suit
        self.chips_bonus = chips_bonus
        self.mult_bonus = mult_bonus
        self.enhancement = enhancement
        self.art = self.art_factory(suit, rank, enhancement)

    def __str__(self) -> str:
        return self.art

    def __repr__(self) -> str:
        return self.__str__()

    def is_face_card(self):
        return self.rank in [11, 12, 13]


class TXTCard(Card):
    suits = "hdcs"
    suits_map = {s: i for i, s in enumerate(suits)}
    figures = "jqk"
    joker = "**"
    ranks = [hex(r)[-1] for r in range(1, 10 + 1)] + list(figures)
    ranks_map = {r: i for i, r in enumerate(ranks, start=1)}
    suit_art = suits
    ranks_art = [None] + ranks
    joker_art = "**"

    @classmethod
    def art_factory(cls, suit, rank, enhancement=CardEnhancement.NONE):
        if suit is None and rank is None:
            art = cls.joker
        else:
            art = cls.ranks[rank-1] + cls.suits[suit]
        return cls.color_art(art, suit=suit, rank=rank, enhancement=enhancement)

    @classmethod
    def suit_from_art(cls, art):
        clean_art = cls.clean_art(art)
        if clean_art == cls.joker:
            return None
        return cls.suits_map[clean_art[1]]

    @classmethod
    def rank_from_art(cls, art):
        clean_art = cls.clean_art(art)
        if clean_art == cls.joker:
            return None
        return cls.ranks_map[clean_art[0]]


class UTFCard(Card):
    # cards_map = {
    #     "back": "🂠",  # \U0001F0A0
    #     "come": "🂱🂲🂳🂴🂵🂶🂷🂸🂹🂺🂻🂽🂾",  # \U0001F0B1-\U0001F0BE ^\U0001F0BC
    #     "quando": "🃁🃂🃃🃄🃅🃆🃇🃈🃉🃊🃋🃍🃎",  # \U0001F0C1-\U0001F0CE ^\U0001F0CC
    #     "fuori": "🃑🃒🃓🃔🃕🃖🃗🃘🃙🃚🃛🃝🃞",  # \U0001F0D1-\U0001F0DE ^\U0001F0DC
    #     "piove": "🂡🂢🂣🂤🂥🂦🂧🂨🂩🂪🂫🂭🂮",  # \U0001F0A1-\U0001F0AE ^\U0001F0AC
    #     "*": "🂿🃏🃟🃠"  # \U0001F0BF \U0001F0CF \U0001F0DF \U0001F0E0
    # }
    cards_base = 0x01F000

    suits = [0xB0, 0xC0, 0xD0, 0xA0]
    suits_map = {s: i for i, s in enumerate(suits)}
    figures = [0x0B, 0x0D, 0x0E]
    joker = 0xCF
    ranks = list(range(0x01, 0x0A + 0x01)) + list(figures)
    ranks_map = {r: i for i, r in enumerate(ranks, start=1)}
    suit_art = ["♠", "♥", "♣", "♦"]
    ranks_art = [None, "A", "2", "3", "4", "5",
                 "6", "7", "8", "9", "T", "J", "Q", "K"]
    joker_art = "🃏"

    @classmethod
    def art_factory(cls, suit, rank, enhancement=CardEnhancement.NONE):
        if suit is None and rank is None:
            art = chr(cls.cards_base | cls.joker)
        else:
            art = chr(cls.cards_base | cls.suits[suit] | cls.ranks[rank-1])
        return cls.color_art(art, suit=suit, rank=rank, enhancement=enhancement)

    @classmethod
    def suit_from_art(cls, art):
        clean_art = cls.clean_art(art)
        if ord(clean_art) & 0xff == cls.joker:
            return None
        return cls.suits_map[ord(clean_art) & 0xf0]

    @classmethod
    def rank_from_art(cls, art):
        clean_art = cls.clean_art(art)
        if ord(clean_art) & 0xff == cls.joker:
            return None
        return cls.ranks_map[ord(clean_art) & 0x0f]


if cards_mode == "utf":
    CardClass = UTFCard
elif cards_mode == "txt":
    CardClass = TXTCard
else:
    raise NotImplementedError(f"rendering mode {cards_mode!r} not supported")

cards = [CardClass(s, r) for s in range(4) for r in range(1, 13+1)]

assert len(CardClass.suits) == 4, [CardClass.suits, len(CardClass.suits)]
assert len(CardClass.figures) == 3, [CardClass.figures, len(CardClass.figures)]
assert len(CardClass.ranks) == 13, [CardClass.ranks, len(CardClass.ranks)]
assert len(cards) == len(CardClass.ranks) * \
    len(CardClass.suits), [cards, len(cards)]


def sort_hand(hand, reverse=False, suit_first=False, ace_after_king=True):
    if suit_first:
        return sorted(hand, reverse=reverse, key=lambda c: (c.suit, c.sorting_rank if ace_after_king else c.rank))
    else:
        return sorted(hand, reverse=reverse, key=lambda c: (c.sorting_rank if ace_after_king else c.rank, c.suit))
