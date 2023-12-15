def load(data, repeat=1):
    field, counts = data.split()
    counts = tuple([int(c) for c in counts.split(",")]) * repeat
    field = "?".join([field] * repeat)
    return field, counts


def match(a, b):
    """
    Compare two fields and return True if they match.
    """
    # different length == False
    if not len(a) == len(b):
        return
    # check each value
    for a, b in zip(a, b):
        # ? is undefined so skip
        if a == "?" or b == "?":
            continue
        # differnce, return False
        if not a == b:
            return False
    # all match
    return True


def process_start(field, counts):
    """
    Process a field and counts to remove unambiguous information from the beginning.
    Any impossible arrangements will throw a ValueError.
    """

    # if counts is empty
    if not counts:
        # and there are some left to count in field
        if field.count("#"):
            # raise an error
            raise ValueError("Impossible arrangement")
        # otherwise both are finished
        return "", tuple()

    # walk through field
    while field and counts:

        # get value at position
        x = field[0]

        # "?" found, break
        if x == "?":
            break

        # ".", can skip to next
        if x == ".":
            # trim the field by 1
            field = field[1:]
            continue

        # "#" so take next block, determined by counts
        count = counts[0]
        counts = counts[1:]

        # "#" block overlaps a "."
        if "." in field[:count]:
            raise ValueError("Impossible arrangement. # block overlaps '.'")

        # check perfectly reached end of field
        if count == len(field):
            # if there are any counts left it will raise an exception below
            field = ""
            break

        if (count + 1) > len(field):
            raise ValueError("Impossible arrangement. Count longer than field.")

        if field[count] == "#":
            raise ValueError("Impossible arrangement. No buffer after # block.")

        # trim the field, taking an extra one for the buffer
        field = field[count + 1 :]

    if counts and not field:
        raise ValueError("Impossible arrangement. Counts left but no field.")

    return field, counts


def process_end(field, counts):
    """
    Remove unambiguous data from the end of a field and counts.
    Reverses, sends through process_start and reverses again.
    """
    field, counts = process_start(field[::-1], counts[::-1])
    return field[::-1], counts[::-1]


_CPA_CACHE = {}


def count_possible_arrangements_cached(cpa_func):
    """
    Decorator for the count_possible arrangements to implement cache.
    Uses the _CPA_CACHE dictionary to store values and exceptions.
    """

    def cache_wrapped_func(field, counts):
        # generate a key
        cache_key = field, counts

        # look in the cache
        cached_value = _CPA_CACHE.get(cache_key, None)
        if cached_value is not None:
            # raise the exception or return the value
            if type(cached_value) == ValueError:
                raise cached_value
            return cached_value

        # execute the function
        try:
            val = cpa_func(field, counts)
            # execution success
            _CPA_CACHE[cache_key] = val
            return val
        except ValueError as e:
            # exception thrown, save it
            _CPA_CACHE[cache_key] = e
            raise e

    return cache_wrapped_func


@count_possible_arrangements_cached
def count_possible_arrangements(field, counts):
    """
    Count the possible arrangements for the given fiels and counts.
    uses decorator to cache results and exceptions for signficiant speedup.
    """

    # remove unambiguous from beginning
    field, counts = process_start(field, counts)

    # exhausted the field, check the counts
    if not field:
        if not counts:
            # also exhausted the counts
            return 1
        else:
            raise ValueError("Impossible arrangement. Counts left but no field.")

    # exhausted the counts (but not field)
    if not counts:
        # any extra # is a problem
        if field.count("#"):
            raise ValueError("Impossible arrangement. Field left but no counts.")
        # otherwise in acceptable condition
        return 1

    # only one counts value
    if len(counts) == 1:
        # make sure there is enough space to fit
        for part in field.split("."):
            if len(part) >= counts[0]:
                break
        else:
            # no possible outcomes
            raise ValueError("Impossible arrangement. No valid outcomes.")

    # amount of space after bunched everything up as close as possible
    min_required_length = sum(counts) + len(counts) - 1
    wiggle_room = len(field) - min_required_length

    if wiggle_room == 0:
        # generate only possible pattern
        pattern = ".".join("#" * count for count in counts)
        if match(pattern, field):
            # perfect match!
            return 1
        raise ValueError("Impossible arrangement. Pattern does not match.")

    if wiggle_room < 0:
        # impossible situation
        raise ValueError("Impossible arrangement. Insuffient field for counts.")

    # try putting a . at the start
    try:
        unbroken = count_possible_arrangements(field[1:], counts[:])
    except ValueError:
        unbroken = 0

    # try putting a # at the start

    try:
        broken = count_possible_arrangements("#" + field[1:], counts[:])
    except ValueError:
        broken = 0

    return broken + unbroken


def go():
    data_list = list()

    from DataSample import DAY_12 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_12 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        for repeat in (1, 5):
            print(name, "Part 1" if repeat == 1 else "Part 2")

            running_total = 0
            for row in data.splitlines():
                row = row.strip()
                if not row:
                    continue

                field, counts = load(row, repeat)
                print(" ", field, counts)

                # remove duplicated "."
                while ".." in field:
                    field = field.replace("..", ".")

                field, counts = process_end(field, counts)
                # don't need to process start, this happens in the function

                # get arrangement count
                arrangements = count_possible_arrangements(field, counts)
                running_total += arrangements
                print("    Posible arrangements:", arrangements)

            print("Total arangement count", running_total)


if __name__ == "__main__":
    go()
