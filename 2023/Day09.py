import numpy


def differences(a):
    """
    Calculate difference between adjacent elements in array.
    """
    a = numpy.asarray(a)
    return a[1:] - a[:-1]


def reduce(a):
    """
    Calculate successive differences until all differences are zero.
    Return all differences.
    """
    depths = [a.copy()]
    # N.B. not sum due to symmetric values about zero
    while not all(a == 0):
        a = differences(a)
        depths.append(a.copy())
    return depths


def extend_values(a):
    """
    Analyse the gaps between numbers in an array and calculate the previous and next values in the sequence.
    """
    # initialise
    next_val = 0
    prev_val = 0

    # reduce the differences between values to zero
    # reverse the values
    reduction = reduce(a)

    # walk up the reduction adding the relevant values
    for r in reduction[::-1][1:]:
        next_val = r[-1] + next_val
        prev_val = r[0] - prev_val

    return next_val, prev_val


def go():
    data_list = list()

    from DataSample import DAY_9 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_9 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:

        print(name)

        running_total_next = 0
        running_total_prev = 0

        # load the sequence
        for line in data.splitlines():
            line = line.strip()

            # skip empty levels
            if not line:
                continue

            # load sequence from line
            seq = numpy.asarray(line.split(), int)

            # calculate extended values
            next_val, prev_val = extend_values(seq)

            # update running totals
            running_total_next += next_val
            running_total_prev += prev_val

            if "Sample" in name:
                print(" ", prev_val, "<-", line, "->", next_val)

        print("  Total of forward values:", running_total_next)
        print("  Total of backward values:", running_total_prev)


if __name__ == "__main__":
    go()
