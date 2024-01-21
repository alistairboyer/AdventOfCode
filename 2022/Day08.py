import io
import numpy
from typing import Set, Tuple


def visible_from_edge(forest: numpy.ndarray) -> Set[Tuple[int, int]]:
    # initialise visible locations
    visible_locations = set()
    # initialise slices default - return whole forest
    slices_default = [slice(None)] * forest.ndim

    for axis in range(0, forest.ndim):
        # get max along current axis for breaking (see later)
        max_along_axis = forest.max(axis)

        # Get generator to address each line - can stop one early because last row is always seen from other side
        # go from low to high
        range_lth = range(0, forest.shape[axis] - 1)
        # go from high to low
        range_htl = range(forest.shape[axis] - 1, 0, -1)
        # consider each of the ranges
        for gen in (range_lth, range_htl):
            # init rolling max
            rolling_max = numpy.zeros(forest.shape[axis], dtype="int8") - 1
            # iterate over range
            for i in gen:
                # get current line
                current_line = numpy.take(forest, i, axis)
                # compare current with rolling max and get location with numpy.where
                new_visible = numpy.asarray(
                    numpy.where(current_line > rolling_max)
                ).flatten()
                # convert back to array indices
                for location_1d in new_visible:
                    # convert numpy.where back to usual location
                    location_2d = [i] * forest.ndim
                    location_2d[1 - axis] = location_1d
                    visible_locations.add(tuple(location_2d))

                # update maximum values
                numpy.maximum(rolling_max, current_line, out=rolling_max)

                # break if all at max
                if (rolling_max >= max_along_axis).all():
                    break

    return visible_locations


def visibility_at(forest: numpy.ndarray, i: int, j: int) -> int:
    # init score
    score = 1
    # get value
    value = forest[i, j]
    # look in each direction
    for view, reverse in [
        (forest[:i, j], True),  # up
        (forest[i, :j], True),  # left
        (forest[i + 1 :, j], False),  # down
        (forest[i, j + 1 :], False),  # right
    ]:
        # reverse where neessary
        if reverse:
            view = view[::-1]
        # convert to bool
        view_test = view < value
        # at edge
        if view_test.size == 0:
            continue
        # all lower then return size of view
        if view_test.all():
            score *= view_test.size
            continue
        # otherwise find first instance of False
        # include blocking tree -> +1
        score *= numpy.argmin(view_test) + 1

    return score


def go():
    data_list = list()

    from DataSample import DAY_08 as SAMPLE

    data_list.append(("Sample", SAMPLE))
    try:
        from DataFull_ import DAY_08 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        forest = numpy.genfromtxt(io.StringIO(data), delimiter=1, dtype="int8")
        print(forest)
        print()

        # part 1
        visible_locations = visible_from_edge(forest)
        forest_visible = numpy.zeros(forest.shape, dtype="int8") - 1
        for i, j in visible_locations:
            forest_visible[i, j] = forest[i, j]
        if "Sample" in name:
            print(forest_visible)
        print(len(visible_locations), "visible trees")
        print()

        # part 2
        visibilities = numpy.zeros(forest.shape, dtype=int)
        for loc in numpy.ndindex(forest.shape):
            visibilities[loc] = visibility_at(forest, *loc)
        if "Sample" in name:
            print(visibilities)
        print(
            "Maximum visibility with score",
            visibilities.max(),
            "at",
            numpy.asarray(numpy.where(visibilities == visibilities.max())).transpose(),
        )
        print()


if __name__ == "__main__":
    go()
