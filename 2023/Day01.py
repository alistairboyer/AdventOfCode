import re

# spelled out numbers
SPELLED_OUT = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def first_and_last_digit_joiner(first, last=None):
    """
    Calculate an integer value based on two numbers either in digit or written form.
    Joins the two numbers together or repeats the first twice if no second digit is supplied.
    Returns 0 if the first is falsy.
    """
    # if first is falsy then value is zero
    if not first:
        return 0
    # look up spelled out values for first value
    first = SPELLED_OUT.get(first, first)
    # look up spelled out values for last value
    if last:
        last = SPELLED_OUT.get(last, last)
    # if supplied last is False then use first instead
    else:
        last = first
    return int("".join((first, last)))


def first_and_last_regex_match(text: str, match: str = r"\d") -> int:
    """
    Find the first and last match on each line of a str using regex.
    Default match is \d to find digits.
    """
    # regex to match first and last
    # first uses negative lookahead to allow overlap
    regex = re.compile(f"(?=({match})).*({match})", re.MULTILINE)
    # execute the regex search
    matches = regex.findall(text)
    return matches


def go():
    data_list = list()

    from DataSample import DAY_1 as SAMPLE

    data_list.append(("Part 1 Sample", SAMPLE))

    from DataSample import DAY_1_PART2 as SAMPLE_PART_2

    data_list.append(("Part 2 Sample", SAMPLE_PART_2))

    try:
        from DataFull_ import DAY_1 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    spelled_pattern = "|".join(["\d"] + list(SPELLED_OUT))

    # load the data
    for name, data in data_list:

        # print data name
        print(name)

        # find matches
        matches = first_and_last_regex_match(data)
        # convert to ints
        matches = [first_and_last_digit_joiner(*match) for match in matches]
        # print the ints for the sample data
        if ("Sample") in name:
            print(" ", matches)
        # print the sum
        print("  Digit only:", sum(matches))

        # find matches including spelled out numbers
        matches = first_and_last_regex_match(data, spelled_pattern)
        # convert to ints
        matches = [first_and_last_digit_joiner(*match) for match in matches]
        # print the ints for the sample data
        if ("Sample") in name:
            print(" ", matches)
        # print the sum
        print("  Digit and spelled out:", sum(matches))

        print()


if __name__ == "__main__":
    go()
