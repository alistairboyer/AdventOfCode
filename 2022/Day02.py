import functools

WIN_POINTS = 6
DRAW_POINTS = 3
LOSE_POINTS = 0

OUTCOMES = {"X": LOSE_POINTS, "Y": DRAW_POINTS, "Z": WIN_POINTS}


class Roshambo:
    """
    A class to represent value of rock, paper, scissors.
    Logical comparison

    Initialise
    ==========
        [case insensitive]
        rock:     pass a value of 'rock', 'a', 'x'
        paper:    pass a value of 'paper', 'b', 'y'
        scissors: pass a value of 'scissors', 'c', 'z'

    Properties
    ==========
        value (srt)
            the value of this choice
        score (int)
            score associated with this choice
        beats (str)
            the choice that this one beats
        beaten_by (str)
            the choice beats this one
    """

    def __init__(self, val):
        self.value = {
            "rock": "rock",
            "paper": "paper",
            "scissors": "scissors",
            "a": "rock",
            "b": "paper",
            "c": "scissors",
            "x": "rock",
            "y": "paper",
            "z": "scissors",
        }[val.casefold()]

    @property
    def score(self):
        return {
            "rock": 1,
            "paper": 2,
            "scissors": 3,
        }[self.value]

    @property
    def beats(self):
        return {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock",
        }[self.value]

    @property
    def beaten_by(self):
        return {
            "scissors": "rock",
            "rock": "paper",
            "paper": "scissors",
        }[self.value]

    def __gt__(self, other):
        return self.beats == other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return f"[{self.value}]"


@functools.lru_cache
def score(opponent_chr, me_chr):
    """
    Calculate my rock, paper, scissors score with choices
    indicated by opponent and me.
    """
    opponent = Roshambo(opponent_chr)
    me = Roshambo(me_chr)
    if me == opponent:
        return me.score + DRAW_POINTS
    if me > opponent:
        return me.score + WIN_POINTS
    return me.score + LOSE_POINTS


@functools.lru_cache
def score_with_outcome(opponent_chr, outcome_chr):
    """
    Calculate my rock, paper, scissors score with choices
    indicated by opponent the desired outcome.
    """
    opponent = Roshambo(opponent_chr)
    if outcome_chr == "X":
        me = Roshambo(opponent.beats)
    elif outcome_chr == "Y":
        me = Roshambo(opponent.value)
    else:
        me = Roshambo(opponent.beaten_by)
    return me.score + OUTCOMES[outcome_chr]


def go():
    data_list = list()

    from DataSample import DAY_02 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_02 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(
            f"{name}: Part 1 score =",
            sum((score(*line.split()) for line in data.splitlines() if line)),
        )
        print(
            f"{name}: Part 2 score =",
            sum(
                (
                    score_with_outcome(*line.split())
                    for line in data.splitlines()
                    if line
                )
            ),
        )


if __name__ == "__main__":
    go()
