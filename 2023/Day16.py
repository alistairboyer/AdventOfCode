import numpy
import collections


class Beam:
    N = 1 << 0
    E = 1 << 1
    S = 1 << 2
    W = 1 << 3
    VERTICAL = N | S
    HORIZONTAL = E | W

    @classmethod
    def beam_generator(cls, c, direction):
        """
        Yield directions based on a value and a direction.
        """
        # nothing here - continue as before
        if c == ".":
            yield direction

        # forward slash mirror
        if c == "/":
            yield {
                cls.N: cls.E,
                cls.E: cls.N,
                cls.W: cls.S,
                cls.S: cls.W,
            }[direction]

        # backslash mirror
        if c == "\\":
            yield {
                cls.N: cls.W,
                cls.W: cls.N,
                cls.E: cls.S,
                cls.S: cls.E,
            }[direction]

        # horizontal beam splitter
        if c == "-":
            if direction & cls.HORIZONTAL:
                yield direction
            else:
                yield from [cls.E, cls.W]

        # vertical beam splitter
        if c == "|":
            if direction & cls.VERTICAL:
                yield direction
            else:
                yield from [cls.N, cls.S]

    # vectors to walk in each direction
    DELTAS = {
        N: (-1, 0),
        E: (0, 1),
        S: (1, 0),
        W: (0, -1),
    }

    # str representation of the directions
    STR = {
        N: "↑",
        S: "↓",
        E: "→",
        W: "←",
        N | S: "↕",
        W | E: "↔",
        N | E: "└",
        N | W: "┘",
        S | E: "┌",
        S | W: "┐",
    }

    @classmethod
    def step(cls, loc, direction):
        """
        Step a tuple location in the given direction.
        """
        delta = cls.DELTAS[direction]
        return tuple(x + dx for x, dx in zip(loc, delta))


class Network:
    def __init__(self, data=None):
        if data is not None:
            self.load(data)

    def load(self, data):
        data_list = list()
        for row_data in data:
            if not row_data:
                continue
            data_list.append(list(row_data))
        self.data = numpy.asarray(data_list, str)

    def __getitem__(self, val):
        # allow easy indexing of data
        return self.data[val]

    @staticmethod
    def print_array(a, default="*"):
        """
        Convert an array to str. Values not included in Pipe.STR replaced with default.
        """
        return "\n".join("".join([Beam.STR.get(x, default) for x in row]) for row in a)

    def __str__(self):
        return "\n".join("".join(row) for row in self.data)

    def journey_str(self):
        """
        Convert journey to str.
        """
        return self.print_array(self.journey, ".")

    def reset_journey(self):
        """
        Reset a journey log and empty the beams.
        """
        self.journey = numpy.zeros(self.data.shape, int)
        self.beams = collections.deque()

    def log_step(self, loc, direction):
        """
        Log a step in the journey location.
        Raise a ValueError is already been at this location and in this direction.
        """
        if self.journey[loc] & direction:
            raise ValueError("Light already travelled here.")
        self.journey[loc] |= direction

    def _step(self):
        """
        Step the light beam through the network.
        """

        # get a light beam
        loc, direction = self.beams.pop()

        # log the step
        try:
            self.log_step(loc, direction)
        # will raise ValueError if already visited here in this direction
        except ValueError:
            return

        # get the next location
        new_loc = Beam.step(loc, direction)

        # check the bounds
        for x in [0, 1]:
            if new_loc[x] >= self.data.shape[x] or new_loc[x] < 0:
                return

        # get the next direction
        for new_direction in Beam.beam_generator(self.data[new_loc], direction):
            self.beams.append((new_loc, new_direction))

    def walk(self, loc, direction):
        """
        Walk a light path into the maze at a location in a particular direction.
        """
        self.reset_journey()
        for new_direction in Beam.beam_generator(self.data[loc], direction):
            self.beams.append((loc, new_direction))
        while self.beams:
            self._step()


def go():
    data_list = list()

    from DataSample import DAY_16 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_16 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        print()

        print("Part 1")
        n = Network(data.splitlines())
        print(n)
        print("Energising beams")
        n.walk((0, 0), Beam.E)
        print(n.journey_str())
        print((n.journey > 0).sum(), "energised")
        print()

        print("Part 2")
        # brute force bacy!
        max_energised = 0
        max_at = None
        for i in range(n.data.shape[0]):
            # top, south
            n.walk((0, i), Beam.S)
            energised = (n.journey > 0).sum()
            if energised > max_energised:
                max_energised = energised
                max_at = (0, i), Beam.S

            # bottom, north
            n.walk((n.data.shape[0] - 1, i), Beam.N)
            energised = (n.journey > 0).sum()
            if energised > max_energised:
                max_energised = energised
                max_at = (n.data.shape[0] - 1, i), Beam.N

        for i in range(n.data.shape[1]):
            # left, east
            n.walk((i, 0), Beam.E)
            energised = (n.journey > 0).sum()
            if energised > max_energised:
                max_energised = energised
                max_at = (i, 0), Beam.E

            # right, west
            n.walk((i, n.data.shape[1] - 1), Beam.W)
            energised = (n.journey > 0).sum()
            if energised > max_energised:
                max_energised = energised
                max_at = (i, n.data.shape[1] - 1), Beam.W

        loc, dirn = max_at
        print("Max energised", max_energised, "at", loc, "pointing", Beam.STR[dirn])


if __name__ == "__main__":
    go()
