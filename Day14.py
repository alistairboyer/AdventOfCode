import numpy


class RockType:
    NONE = "."
    SQUARE = "#"
    ROUND = "O"


def load(data):
    rows = list()
    for row in data:
        if not row:
            continue
        rows.append([c for c in row])
    return numpy.asarray(rows, str)


def roll_sequence(sequence):
    """
    Rolls a sequence to the left.
    """

    def process_buffer():
        """
        Count the number of round rocks and return that many plus spaces to make up the difference.
        """
        number_round = buffer.count(RockType.ROUND)
        return [RockType.ROUND] * number_round + [RockType.NONE] * (
            len(buffer) - number_round
        )

    # store the information between square rocks
    buffer = list()

    # iterate over the sequence
    for c in sequence:
        # if it is a square rock, it doesnt move
        if c == RockType.SQUARE:
            # process the buffer
            yield from process_buffer()
            # reset the buffer
            buffer = list()
            yield RockType.SQUARE
            continue
        # save the information in the buffer
        buffer.append(c)
    yield from process_buffer()


def roll(table, direction):
    """
    Roll the rocks in a given direction.
    """
    result = table

    # use roll_sequence that rolls to left

    # need to convert the table according to desired direction

    # for N, S need to transpose the table
    if direction in {"N", "S"}:
        result = result.T

    # for E, W need to process the data in reverse order
    if direction in {"E", "S"}:
        result = result[..., ::-1]

    # do rolling
    result = numpy.asarray([list(roll_sequence(col)) for col in result])

    # reorient table back to original direction
    # N.B. perform operations in reverse order

    # unreverse
    if direction in {"E", "S"}:
        result = result[..., ::-1]

    # untranspose
    if direction in {"N", "S"}:
        result = result.T

    return result


def calculate_load(collection):
    """
    Calculate the load of round rocks.
    """
    # get total of rocks on each line
    round_rocks_on_each_line = (collection == RockType.ROUND).sum(axis=1)
    # calculate score for each line
    line_score = numpy.linspace(collection.shape[1], 1, collection.shape[1])
    # multiply and sum
    return (round_rocks_on_each_line * line_score).astype(int).sum()


def cycler(sequence, repeat_period=None):
    """
    Yield from a sequence an indefinite number of times.
    """
    # get the repeatin period
    if repeat_period is None:
        repeat_period = len(sequence)
    i = 0
    while True:
        yield sequence[i]
        i = (i + 1) % repeat_period


def find_repeat(sequence):
    """
    Analyse a sequence and find the minimum repeating pattern.
    N.B. Will return the whole sequence if no sub pattern is found.
    """
    for i in range(1, len(sequence)):
        for a, b in zip(sequence, cycler(sequence, i)):
            if not a == b:
                break
        # all match so return pattern
        else:
            return sequence[:i]


def predict(sequence, n, settle_time=None):
    """
    Get nth value form a sequence by extrapolation.
    If n < len(sequence), return the value directly.
    Otherwise use find_repeat to find a repeating pattern and
    then return a value based on that.
    If a repeating pattern was not found raise ValueError.
    """

    # Return the answer directly if in known sequence
    if n < len(sequence):
        return sequence[n]

    # If settle time is not provided use half the sequence length
    # This part of the sequence is ignored due to noise from settling in
    if settle_time is None:
        settle_time = len(sequence) // 2

    # Use find repeat to find a reapeat
    repeat = find_repeat(sequence[settle_time:])

    # If the repatd eosn not appear at least twice, raise a ValueError
    if len(repeat) > (len(sequence) - settle_time) // 2:
        raise ValueError("Repeating sub pattern could not be found")

    print("    Repeating pattern found of length:", len(repeat))
    print("    Repeating pattern starts at:", find_within(repeat, sequence))
    return repeat[(n - settle_time - 1) % len(repeat)]


def find_within(needle, haystack):
    """
    Find position when a needle sequence starts within a haystack.
    Returns None if needle not found.
    """
    for i in range(len(haystack) - len(needle)):
        for a, b in zip(needle, haystack[i:]):
            if not a == b:
                break
        # all match
        else:
            return i
    return None


def go():
    data_list = list()

    from DataSample import DAY_14 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_14 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        rocks = load(data.splitlines())
        if "Sample" in name:
            print("  Loaded", name)
            print(" ", *["".join(r) for r in rocks], sep="\n  ")
            print()

        # part 1
        print("  Part 1")
        print()
        direction = "N"
        rolled = roll(rocks, direction)
        if "Sample" in name:
            print("    Rolled:", direction)
            print("", *["".join(r) for r in rolled], sep="\n    ")
            print()
        rock_load = calculate_load(rolled)
        print("    Load:", rock_load, "after rolling", direction)
        print()

        # part 2
        # obviously this would take too long if actually computed
        # so calculate a smaller number of times and see if there is a repeating sequence
        print("  Part 2")
        print()

        # Initially pattern_search_length was 1000
        # With 500 iterations allowed for settling
        # But the pattern actually settles in after 164 times
        # and repeats with sequence of 28
        # So running 300 times and ignoreing the first 200 results is ample
        pattern = list()
        pattern_search_length = 300

        # repeat the rolling
        for n in range(pattern_search_length):

            # roll in every direction
            for direction in ["N", "W", "S", "E"]:
                rocks = roll(rocks, direction)

            # save the load information
            pattern.append(calculate_load(rocks))

            # print out information for the first few runs
            if n < 3:
                if "Sample" in name:
                    print("    Cycle", n + 1)
                    print("     ", *["".join(r) for r in rocks], sep="\n      ")
                    print()
                    print("      Load =", calculate_load(rocks))
                    print()

        n = 1_000_000_000
        # make a predition based on a repeating cycle
        prediction = predict(pattern, n, settle_time=200)
        print("    Load at", n, "is", prediction)
        print()


if __name__ == "__main__":
    go()
