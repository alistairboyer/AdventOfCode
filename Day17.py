import numpy
import collections


class Cardinal:
    N = 1 << 0
    E = 1 << 1
    S = 1 << 2
    W = 1 << 3

    _DELTAS = {
        N: (-1, 0),
        E: (0, 1),
        S: (1, 0),
        W: (0, -1),
    }

    _STR = {
        N: "N",
        E: "E",
        S: "S",
        W: "W",
    }

    @classmethod
    def str(cls, value):
        return cls._STR.get(value, "-")

    @classmethod
    def delta(cls, value):
        return cls._DELTAS[value]

    @classmethod
    def numpy(cls):
        return numpy.asarray(cls.delta(), dtype="int8")

    @classmethod
    def reverse(cls, value):
        return (value >> 2) or (value << 2)

    @classmethod
    def rotateCW(cls, value):
        return ((value << 1) & 0b1111) or cls.N

    @classmethod
    def rotateCCW(cls, value):
        return value >> 1 or cls.W

    @classmethod
    def step(cls, value, location, step_count=1):
        deltax, deltay = cls.delta(value)
        return location[0] + step_count * deltax, location[1] + step_count * deltay


class RouteScore:
    """
    The score is an array of integer numbers of the minimum score of Paths that left the location to a given direction.
    """

    def __init__(self, shape, max_inertia):
        max_inertia = int(max_inertia)

        # for each of the cardinal directions in order
        # save a score for leavgin with the specified number of steps available
        self.possible_steps = list()
        for direction in [Cardinal.N, Cardinal.E, Cardinal.S, Cardinal.W]:
            for n in range(1, max_inertia + 1):
                self.possible_steps.append((direction, n))
        # also save this as a numpy array for indexing
        self.possible_steps_numpy = numpy.asarray(self.possible_steps, dtype="uint8")

        # initialise the score to the max value of the datatype
        self.score = numpy.zeros(shape + (len(self.possible_steps),), dtype="int32")
        self.score[...] = numpy.iinfo(self.score.dtype).max

        # set edge limits
        for n in range(max_inertia):
            self.score[
                n,
                slice(None),
                slice(
                    self.possible_steps.index((Cardinal.N, n + 1)),
                    1 + self.possible_steps.index((Cardinal.N, max_inertia)),
                ),
            ] = -1
            self.score[
                :,
                n,
                slice(
                    self.possible_steps.index((Cardinal.W, n + 1)),
                    1 + self.possible_steps.index((Cardinal.W, max_inertia)),
                ),
            ] = -1
            self.score[
                (-1 - n),
                :,
                slice(
                    self.possible_steps.index((Cardinal.S, n + 1)),
                    1 + self.possible_steps.index((Cardinal.S, max_inertia)),
                ),
            ] = -1
            self.score[
                :,
                (-1 - n),
                slice(
                    self.possible_steps.index((Cardinal.E, n + 1)),
                    1 + self.possible_steps.index((Cardinal.E, max_inertia)),
                ),
            ] = -1

    def update_if_lower(self, location, direction, nsteps, value):
        """
        Update the score at a given location, laeving in a direction with nsteps to be the value if lower than the current value.
        """
        if value < self.score[location][self.possible_steps.index((direction, nsteps))]:
            self.score[location][self.possible_steps.index((direction, nsteps))] = value

    def get_path_steps(self, path):
        # filter based on path length
        score_step_filter = path.score < self.score[path.location]
        # filter based on path options
        path_step_filter = path.possible_step_filter()
        # combine filters
        filter = score_step_filter & path_step_filter
        if not filter.any():
            return []
        # update the score to reflect this path
        self.score[path.location][filter] = path.score
        # return the new steps
        return self.possible_steps_numpy[filter]


class LavaMap:
    def __init__(self, data=None) -> None:
        if data is not None:
            # contiguous single integer values
            self.data = numpy.genfromtxt(data, delimiter=1, dtype="uint8")

    def __getitem__(self, val):
        return self.data[val]

    def walk(self, start_location, end_location):
        # initialise a score at every location in the map
        scores = RouteScore(self.data.shape, Path.MAX_INERTIA)

        # init the paths to follow from the start point
        # paths_to_follow = collections.deque([Path(start_location)])
        paths_to_follow = [Path(start_location)]
        paths_arrived = list()
        best_so_far = 9999999999999999999999999
        # continue execution while paths are available to follow
        loop_count = 0

        while paths_to_follow:
            loop_count += 1

            # focus on the shortest paths but only sort every 100 cycles
            if loop_count % 100 == 0:
                paths_to_follow.sort(key=lambda path: path.score)

            path = paths_to_follow[0]
            paths_to_follow = paths_to_follow[1:]

            # don't follow paths worse than the best
            if path.score > best_so_far:
                continue

            # path has reached end location
            if path.location == end_location:
                best_so_far = min(path.score, best_so_far)
                paths_arrived.append(path)
                continue

            # get directions and number of steps to walk
            for direction, n_steps in scores.get_path_steps(path):
                new_location = path.location
                new_score = path.score
                new_history = None
                # new_history = path.history[:]

                # take intermediate steps
                for n in range(1, 1 + n_steps):
                    new_location = Cardinal.step(direction, new_location)
                    new_score += self.data[new_location]
                    # new_history.append(new_location)

                    # update best score for squares being stepped over
                    if n >= Path.MIN_INERTIA:
                        for i in range(n, n_steps):
                            scores.update_if_lower(
                                new_location, direction, n_steps - i, new_score
                            )

                new_path = Path(new_location, new_score, direction, new_history)
                paths_to_follow.append(new_path)

        paths_arrived.sort(key=lambda path: path.score)
        best_path = paths_arrived[0]
        return best_path


class Path:
    MIN_INERTIA = 1
    MAX_INERTIA = 3

    def __init__(self, location, score=0, direction=None, history=None):
        self.location = location
        self.score = score
        self.direction = direction
        self.history = history

    def __str__(self):
        return f"Path going {Cardinal.str(self.direction)} at ({self.location}) score={self.score}, history=[{self.history}]."

    def possible_step_filter(self):
        """
        Return the possible steps that can be taken.
        All possible forward steps in a given direction are considered at once and it is not permitted to go backwards.
        Therefore, only steps perpendicular to the current direction are possible.
        """
        possible_steps = []
        for direction in [Cardinal.N, Cardinal.E, Cardinal.S, Cardinal.W]:
            direction_possible = True
            if self.direction is not None:
                if direction == self.direction:
                    direction_possible = False
                elif direction == Cardinal.reverse(self.direction):
                    direction_possible = False
            possible_steps += [False] * (self.__class__.MIN_INERTIA - 1)
            possible_steps += [direction_possible] * (
                self.__class__.MAX_INERTIA - self.__class__.MIN_INERTIA + 1
            )
        return possible_steps


def go():
    data_list = list()

    from DataSample import DAY_17 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_17 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print()
        print(name)
        lava = LavaMap(data.splitlines())
        start_location = (0, 0)
        end_location = tuple(numpy.asarray(lava.data.shape, int) - 1)

        Path.MIN_INERTIA = 1
        Path.MAX_INERTIA = 3
        print("  Directional inertia", Path.MIN_INERTIA, "-", Path.MAX_INERTIA)
        print("  Best path has score", lava.walk(start_location, end_location).score)
        print()
        Path.MIN_INERTIA = 4
        Path.MAX_INERTIA = 10
        print("  Directional inertia", Path.MIN_INERTIA, "-", Path.MAX_INERTIA)
        print("  Best path has score", lava.walk(start_location, end_location).score)


if __name__ == "__main__":
    go()
