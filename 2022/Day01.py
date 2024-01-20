import io
from typing import List


def max_elf(text_input: str, n: int = 1) -> List[int]:
    """
    Process text containing numbers on separate lines
        in groups separated by empty lines.
    Returns the top n group sum values.
    """

    # use list so can update by reference in update_totals
    # totals[0] is current total
    # totals[1] is the top n totals
    totals = [0, [0] * n]

    # update the totals
    def update_totals():
        # if nothing in total, preloaded with zero so return
        if not totals[0]:
            return
        # new total is higher than lowest in lost
        if totals[0] > totals[1][0]:
            # save the new total
            totals[1][0] = totals[0]
            # udpate the order of totals
            totals[1].sort()
        # reset current total back to zero
        totals[0] = 0

    # turn text into iterable
    i = iter(io.StringIO(text_input))
    for line in i:
        # remove whitespace
        line = line.strip()

        # break between data -> update totals
        if not line:
            update_totals()
            continue

        # update the total
        totals[0] += int(line)

    # update at end of iteration
    else:
        update_totals()

    # return top n totals
    return totals[1]


def go():
    data_list = list()

    from DataSample import DAY_01 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_01 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(f"{name}: largest group value:", max_elf(data, 1)[0])
        print(
            f"{name}: largest 3 group values:",
            max_elf(data, 3),
            "sum:",
            sum(max_elf(data, 3)),
        )


if __name__ == "__main__":
    go()
