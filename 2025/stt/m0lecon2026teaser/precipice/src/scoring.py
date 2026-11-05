rank_chips = {r: 11 if r == 1 else 10 if r > 10 else r for r in range(1, 13+1)}

base_scores = {
    # When no other hand is possible, scores whichever played card is the highest rank.
    "high_card": [5, 1],
    "pair": [10, 2],  # Two cards with a matching rank. Suits may be different.
    # Two cards with a matching rank and two cards with a different matching rank. Suits may differ.
    "two_pair": [20, 2],
    # Three cards with a matching rank. Suits may be different.
    "three_of_a_kind": [30, 3],
    # Five cards with ranks that are in consecutive order. Suits may be different.
    "straight": [30, 4],
    "flush": [35, 4],  # Five cards of any rank that all share the same suit.
    # Three cards with a matching rank and two cards with a different matching rank, with cards from at least two or more suits.
    "full_house": [40, 4],
    # Four cards with a matching rank. Suits may be different.
    "four_of_a_kind": [60, 7],
    # Five cards in consecutive order that all share the same suit.
    "straight_flush": [100, 8],
    # A Straight Flush that contains an Ace, King, Queen, Jack, and 10 on the same suit.
    "royal_flush": [100, 8],
    # Five cards with the same rank which are not all the same suit.
    "five_of_a_kind": [120, 12],
    # Three cards with the same rank, and two cards with the same rank, all from a single suit.
    "flush_house": [140, 14],
    # Five cards with the same rank and same suit.
    "flush_five": [160, 16],
}

antes = [
    0,
    100,
    300,
    800,
    2000,
    5000,
    11000,
    20000,
    35000,
    50000,
    110000,
    1560000,
    17200000,
    1300000000,
    147000000000,
    12.9e13,
    17.7e16,
    18.6e20,
    14.2e25,
    19.2e30,
    19.2e36,
    24.3e43,
    29.7e50,
    21.0e59,
    25.8e67,
    21.6e77,
    22.4e87,
    21.9e98,
    28.4e109,
    22.0e122,
    22.7e135,
    32.1e149,
    39.9e163,
    32.7e179,
    34.4e195,
    34.4e212,
    32.8e230,
    31.1e249,
    32.7e268,
    34.5e288,
    34.8e309,
]
