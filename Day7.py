class Game:
    def __init__(self, data=None, use_jokers=False) -> None:
        self.hands = list()
        self._HandClass = HandWithJokers if use_jokers else Hand
        if data is not None:
            self.load(data)

    def load(self, data):      
        for line in data:
            if not line:
                continue           
            self.hands.append(self._HandClass(*line.split()))

    def sorted(self, reverse=True):
        """
        Return sorted hands. Best first if reverse is True.
        """
        return sorted(self.hands, key=lambda hand: hand.sorting_key(), reverse=reverse)

    def score(self):
        """
        Calculate score. The hand rank multiplied by the wager for each hand.
        """
        running_total = 0
        for n, hand in enumerate(self.sorted(reverse=False)):
            running_total += hand.wager * (n + 1)
        return running_total

    def __str__(self):
        return "\n".join(str(hand) for hand in self.sorted())


class Hand:
    CARD_VALUES = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}

    def __init__(self, cards, wager) -> None:
        self.cards = list(cards)
        self.wager = int(wager)

    def rank(self):
        """
        Calculate rank of hand:
            7: 5 of a kind
            6: 4 of a kind
            5: full house
            4: 3 of a kind
            3: two pair
            2: pair
            1: high card
        """

        # calculate the counts of each card
        card_counts = [(self.cards.count(x), x) for x in set(self.cards)]

        # sort, biggest group of cards first
        card_counts.sort(reverse=True)

        # ititialise rank value based on size of largest set
        rank_value = (2 * card_counts[0][0]) - 2

        # check for second pair, for two pair and full house
        # add one to rank value
        if len(card_counts) > 1 and card_counts[1][0] == 2:
            rank_value += 1

        # clip lowest and highest values to fit into nice order
        return max(min(rank_value, 7), 1)

    def card_score(self):
        """
        A tuple of numeric card values.
        """
        return tuple(self.number_value(c) for c in self.cards)

    def sorting_key(self):
        """
        A sortable tuple using hand rank and card values.
        """
        return (self.rank(), *self.card_score())

    def number_value(self, card):
        """
        Convert a str card to its numeric equivalent.
        """
        try:
            # get integer conversion
            return int(card)
        except ValueError:
            # lookup integer value
            return self.CARD_VALUES[card]

    def __str__(self):
        return f"{''.join(self.cards)} {self.wager}"


class HandWithJokers(Hand):
    CARD_VALUES = {"T": 10, "J": 0, "Q": 12, "K": 13, "A": 14}

    def rank(self):
        """
        Calculate rank of hand, jokers are wild:
            7: 5 of a kind
            6: 4 of a kind
            5: full house
            4: 3 of a kind
            3: two pair
            2: pair
            1: high card
        """

        # get number of jokers
        number_jokers = self.cards.count("J")

        # counta ll the sets of cards, skipping the jokers
        card_counts = [
            (self.cards.count(x), x) for x in set(self.cards) if not x == "J"
        ]
        card_counts.sort(reverse=True)

        # if all jokers, then five of a kind
        if number_jokers == 5:
            return 7
        
        # directly correlate rank to size of largest set
        # boost largest set with the extra jokers
        rank_value = 2 * (card_counts[0][0] + number_jokers) - 2

        # check for second pair, for two pair and full house
        # add one to rank value
        if len(card_counts) > 1 and card_counts[1][0] == 2:
            rank_value += 1
            pass

        # clip lowest and highest values to fit into nice order
        return max(min(rank_value, 7), 1)


def go():
    data_list = list()
    
    from DataSample import DAY_7 as SAMPLE
    data_list.append(("Sample", SAMPLE))
    
    try:
        from DataFull_ import DAY_7 as DATA
        data_list.append(("Full Data", DATA))
    except ImportError:
        pass
   
    for name, data in data_list:

        for use_jokers in {False, True}:
            print(name, "with jokers wild" if use_jokers else "")
            game = Game(data.splitlines(), use_jokers=use_jokers)
            if "Sample" in name:
                print(game)
            print("Score: ", game.score())
            print()

if __name__ == "__main__":
    go()
