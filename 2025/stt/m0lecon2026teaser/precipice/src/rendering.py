from cards import CardClass

clear_char = chr(27) + "[2J"

# clear_char = ""
# print = lambda *args, **kwargs: None


def render(
    hand=None,
    drew=None,
    selected=None,
    header=None,
    message=None,
    score=None,
    hands_discards=None,
    ante=None,
    next_stake=None,
    hand_scoring=None,
    jokers=None,
    jokers_selected=None,
    jokers_in_shop=None,
    jokers_selected_in_shop=None,
    state=None,
    verbose=True
):
    print(clear_char)
    rows = []
    if header is None:
        header = []
    if message is None:
        message = []
    if len(header):
        for row in header:
            rows.append(f" {row.strip()}")
    if verbose:
        if ante is not None:
            rows.append(f" ante: {ante+1}")
    if next_stake is not None:
        if verbose:
            rows.append(f" next stake: {next_stake}")
        else:
            rows.append(f" ~${next_stake}")
    if jokers is not None:
        if jokers_selected is not None:
            assert len(set(jokers) - set(jokers_selected)
                       ) == len(jokers) - len(jokers_selected)
            jokers_selected = set(jokers_selected)
            rows += [""] * 3
            for i, c in enumerate(jokers, start=1):
                l = len(CardClass.clean_art(c.art)) + 1
                if c in jokers_selected:
                    rows[-3] += f" {c.art}"
                    rows[-2] += f" {'^' * l}"
                else:
                    rows[-3] += f" {' ' * l}"
                    rows[-2] += f" {c.art}"
                si = str(i)
                rows[-1] += f"-{si}{' ' * (l-len(si))}"
            if len(jokers_selected):
                value = sum(map(lambda j: j.value, jokers_selected))
                if verbose:
                    rows.append(f" jokers value: ${value}")
                else:
                    rows.append(f" jv${value}")
                if verbose:
                    message.append(f" owned selected jokers ability:")
                for i, c in enumerate(jokers_selected, start=1):
                    message.append(
                        f" -{jokers.index(c)+1}: {c.name}: {c.description} {c.currently(state)}")
        else:
            rows.append("")
            for c in jokers:
                rows[-1] += f" {c.art}"
    if jokers_in_shop is not None:
        if jokers_selected_in_shop is None:
            jokers_selected_in_shop = []
        assert all(joker in jokers_in_shop for joker in jokers_selected_in_shop)
        jokers_selected_in_shop = set(jokers_selected_in_shop)
        rows += [""] * 3
        for i, c in enumerate(jokers_in_shop, start=1):
            l = len(CardClass.clean_art(c.art)) + 1
            if c in jokers_selected_in_shop:
                rows[-3] += f" {c.art}"
                rows[-2] += f" {'^' * l}"
            else:
                rows[-3] += f" {' ' * l}"
                rows[-2] += f" {c.art}"
            si = str(i)
            rows[-1] += f" {si}{' ' * (l-len(si))}"
        if len(jokers_selected_in_shop):
            price = sum(map(lambda j: j.price, jokers_selected_in_shop))
            if verbose:
                rows.append(f" jokers price: ${price}")
            else:
                rows.append(f" jp${price}")
            if verbose:
                message.append(f" shop selected jokers ability:")
            for i, c in enumerate(jokers_selected_in_shop, start=1):
                message.append(
                    f" {jokers_in_shop.index(c)+1}: {c.name}: {c.description} {c.currently(state)}")
    if hand is not None:
        if drew is None:
            drew = []
        assert len(set(hand) & set(drew)) == len(drew)
        if selected is None:
            selected = []
        assert len(set(hand) - set(selected)) == len(hand) - len(selected)
        drew = set(drew)
        selected = set(selected)
        rows += [""] * 3
        for i, c in enumerate(hand, start=1):
            l = len(CardClass.clean_art(c.art))
            if c in selected:
                rows[-3] += f" {c.art}"
                if c in drew:
                    rows[-2] += f" {'^' * l}"
                else:
                    rows[-2] += f" {' ' * l}"
            else:
                if c in drew:
                    rows[-3] += f" {'v' * l}"
                else:
                    rows[-3] += f" {' ' * l}"
                rows[-2] += f" {c.art}"
            si = str(i)
            rows[-1] += f" {si}{' ' * (l-len(si))}"
    if verbose:
        if hands_discards is not None:
            rows.append(
                f" hands/discards: {hands_discards[0]}/{hands_discards[1]}")
        if score is not None:
            rows.append(f" score: {score}")
        if hand_scoring is not None:
            hand_type, chip, mult = hand_scoring
            rows.append(f" hand selected: {hand_type}")
            rows.append(f" hand chips: {chip}")
            rows.append(f" hand mult: {mult}")
            rows.append(f" hand total: {chip*mult}")
    else:
        r = ""
        if hands_discards is not None:
            r += f" {hands_discards[0]}/{hands_discards[1]}"
        if score is not None:
            r += f" ${score}"
        if hand_scoring is not None:
            hand_type, chip, mult = hand_scoring
            r += f" -> {hand_type} ({chip}*{mult}=${chip*mult})"
        if len(r):
            rows.append(r)
    if len(message):
        for row in message:
            rows.append(f" {row.strip()}")
    for r in rows:
        print(r)
