import re


class ScratchCard:
    def __init__(self, id, winning, numbers) -> None:
        self.id = int(id)
        self.winning = set(winning)
        self.numbers = set(numbers)
        self.instances = 1

    @property
    def matches(self):
        """
        Winning numbers
        """
        return self.winning.intersection(self.numbers)

    @property
    def n_matches(self):
        """
        Number of winning numbers
        """
        return len(self.matches)

    @property
    def score(self):
        """
        Score: 2**(number of matches - 1)
        """
        if not self.matches:
            return 0
        return 1 << (self.n_matches - 1)

    @property
    def new_score(self):
        """
        Score: 1 if any matches
        """
        return 1 if self.matches else 0

    @staticmethod
    def from_text(text):
        """
        Parse text to a ScratchCard object
        """
        [card_info, winning, numbers] = re.split(":|\|", text)
        id_number = card_info.split()[-1]
        winning = winning.split()
        numbers = numbers.split()
        return ScratchCard(id_number, winning, numbers)


def load(data):
    cards = dict()
    for line in data:
        if not line.startswith("Card"):
            continue

        card = ScratchCard.from_text(line)
        cards[card.id] = card

    return cards


def go():
    data_list = list()

    from DataSample import DAY_4 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_4 as DATA

        data_list.append(("Full Data", DATA))

    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        cards = load(data.splitlines())

        # part one scoring
        print("  Total score:", sum(card.score for card in cards.values()))

        # part two scoring
        for card in cards.values():
            # increase instances of cards following winning cards
            for n in range(card.n_matches):
                try:
                    cards[card.id + n + 1].instances += card.instances
                except KeyError:
                    # don't duplicate after end of list
                    break

        print(
            "  Card count after duplication:",
            sum(card.instances for card in cards.values()),
        )
        print()


if __name__ == "__main__":
    go()
