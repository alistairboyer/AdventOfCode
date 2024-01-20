import io


def order_ranges(outer, inner):
    """
    Orders two ranges represented by an ordered sequence of two values.
    If an outer and inner range are supplied then the function
        will swap the value where appropraite before returning.
    """
    # Swap if the inner has a lower start and greater or equal end than the outer
    if inner[0] < outer[0] and inner[1] >= outer[1]:
        outer, inner = inner, outer
    # Swap if the inner has an equal start and greater or equal end than the outer
    elif inner[0] == outer[0] and inner[1] > outer[1]:
        outer, inner = inner, outer
    # Return
    return outer, inner


def range_envelop(range_a, range_b) -> bool:
    """
    True if a range, represented by an ordered sequence of two values,
    is completely contained by another range; or False.
    The order of arguments does not matter because the ranges are processed using `order_ranges`.
    """
    # figure out the outer and inner range
    outer, inner = order_ranges(range_a, range_b)
    # check range limits for complete overlap
    return outer[0] <= inner[0] and outer[1] >= inner[1]


def any_overlap(range_a, range_b, *, reorder=True) -> bool:
    """
    True if a range, represented by an ordered sequence of two values,
    has any overlap with another range; or False.
    The order of arguments does not matter because the ranges are processed using `order_ranges`
        unless kwarg "reorder" is False.
    """
    outer, inner = range_a, range_b
    # figure out the outer and inner ranges if desired
    if reorder:
        outer, inner = order_ranges(outer, inner)
    # check the limits for any overlap
    return (outer[0] <= inner[0] <= outer[1]) or (outer[0] <= inner[1] <= outer[1])


def go():
    data_list = list()

    from DataSample import DAY_04 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_04 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)

        total_contained = 0
        total_partial = 0
        for line in io.StringIO(data):
            # strip blank space
            line = line.strip()

            # skip empty lines
            if not line:
                continue

            # parse data into ranges
            ranges = line.split(",")
            range0 = [int(x) for x in ranges[0].split("-")]
            range1 = [int(x) for x in ranges[1].split("-")]

            # check contained
            contained = range_envelop(range0, range1)
            total_contained += int(contained)
            # check partial
            # N.B. no need to reorder because using the contained result
            partial = contained or any_overlap(range0, range1, reorder=False)
            total_partial += int(partial)

            if "Sample" in name:
                print(
                    "   ",
                    line,
                    "complete overlap"
                    if contained
                    else ("partial overlap" if partial else ""),
                )

        print("    Complete overlap =", total_contained)
        print("    Partial overlap =", total_partial)


if __name__ == "__main__":
    go()
