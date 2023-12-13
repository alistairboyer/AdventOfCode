import numpy


class Pipe:
    # use a bit for each cardinal direction and start
    N = 1 << 0
    E = 1 << 1
    W = 1 << 2
    S = 1 << 3
    START = 1 << 4

    # convert str to directions
    TYPES = {
        "|": N | S,
        "-": E | W,
        "L": N | E,
        "J": N | W,
        "7": S | W,
        "F": S | E,
        ".": 0,
        "S": START,
        "│": N | S,
        "─": E | W,
        "└": N | E,
        "┘": N | W,
        "┐": S | W,
        "┌": S | E,
        " ": 0,
    }

    # directions to str
    STR = {
        N | S: "│",
        N | E: "└",
        N | W: "┘",
        E | W: "─",
        S | W: "┐",
        S | E: "┌",
        0: " ",
        START: "S",
    }

    # vectors to walk in each direction
    DELTAS = {
        N: (-1, 0),
        E: (0, 1),
        S: (1, 0),
        W: (0, -1),
    }

    # reverse of each direction
    DIRECTIONS_REVERSED = {
        N: S,
        S: N,
        E: W,
        W: E,
    }

    # names of directions
    NAMES = {
        N: "N",
        E: "E",
        W: "W",
        S: "S",
    }

    @classmethod
    def reverse(cls, p):
        """
        Reverse of given direction.
        """
        return cls.DIRECTIONS_REVERSED[p]

    @classmethod
    def step(cls, loc, direction):
        """
        Step a tuple location in the given direction.
        """
        delta = cls.DELTAS[direction]
        return tuple(x + dx for x, dx in zip(loc, delta))

    @classmethod
    def str(cls, val):
        """
        Convert int value to a str.
        """
        if val == 5:
            return "S"
        ret = ""
        for dirn, name in cls.NAMES.items():
            if val & dirn:
                ret += name
        return ret

    def __new__(cls, direction):
        """
        Convert the given values and return an int.
        """
        return cls.TYPES[direction]


class Network:
    def __init__(self, data=None):
        if data is not None:
            self.load(data)

    def load(self, data):
        data_list = list()
        for row_data in data:
            if not row_data:
                continue
            data_list.append([Pipe(c) for c in row_data])
        self.pipesnp = numpy.asarray(data_list, int)

    @property
    def start(self):
        """
        Find the location tuple of the start point.
        """
        filter = numpy.nonzero(self.pipesnp == Pipe.START)
        return tuple(zip(*filter))

    def __getitem__(self, val):
        # allow easy indexing of data
        return self.pipesnp[val]

    @staticmethod
    def print_array(a, default="*"):
        """
        Convert an array to str. Values not included in Pipe.STR replaced with default.
        """
        return "\n".join("".join([Pipe.STR.get(x, default) for x in row]) for row in a)

    def __str__(self):
        return self.print_array(self.pipesnp)

    def print(self, loc=None, symbol="*"):
        """
        Convert data to str. Replaces data at loc with given symbol.
        """
        a = self.pipesnp.copy()
        if loc is not None:
            a[loc] = -1
        return self.print_array(a, symbol)

    def step(self, loc, direction):
        """
        Take one step in the given direction.
        Returns (new_location, new_direction) or (None, None) if not possible.
        """

        # caluclate reverse of direction
        reverse_direction = Pipe.reverse(direction)

        # check curent location has correct connection
        # can walk in all directions at start
        if not self.pipesnp[loc] == Pipe.START:
            # Can not walk in that direction: no open path from here
            if not self.pipesnp[loc] & direction:
                return None, None

        # go to new direction
        new_loc = Pipe.step(loc, direction)

        # out of bounds
        try:
            _ = self.pipesnp[new_loc]
        except IndexError:
            return None, None

        # check new location has correct connection
        if not self.pipesnp[new_loc] & reverse_direction:
            # Can not walk in that direction: no open path in that direction
            return None, None

        # remove the direction we came from from the direction list
        new_direction = self.pipesnp[new_loc] - reverse_direction
        return new_loc, new_direction

    def walk(self, locs):
        """
        Complete a journey along the pipes starting at the positions given in locs using the step method.
        """
        count = 0
        visited = numpy.zeros_like(self.pipesnp)

        while locs:
            count += 1

            new_locs = list()
            for (loc, d) in locs:
                # get next step
                new_loc, new_d = self.step(loc, d)

                # if not a valid step, continue
                if new_loc is None:
                    continue

                # if already visited, continue
                if visited[new_loc]:
                    continue

                # otherwise, new location so update visited map
                visited[new_loc] = count

                # save the new locs
                new_locs.append((new_loc, new_d))

            # set the locs for the next step
            locs = new_locs

        return visited

    def topology(self, visited):
        """
        Calcualte the topology of the network.
        Requires visited data from the walk method.
        Values: -1 is outside; 1 is inside; 0 is on the network.
        """
        res = list()
        for r, row in enumerate(visited):
            new_row = list()
            # status is -1 at the edge
            status = -1

            last_corner = ""
            for c, char in enumerate(row):
                x = self.pipesnp[r, c]

                # if we are at the start, calculate actual topology of starting position
                if x == Pipe.START:
                    x = 0
                    for d in [Pipe.N, Pipe.E, Pipe.W, Pipe.S]:
                        new_loc = Pipe.step((r, c), d)
                        if visited[new_loc] == 1:
                            x |= d
                    char = Pipe.str(x)

                # on the pipe
                if char:
                    # add 0 to this location
                    new_row.append(0)

                    # horixontal pipe, no topology change
                    if x == Pipe("-"):
                        continue

                    # vertical pipe, change
                    if x == Pipe("|"):
                        status = 0 - status
                        continue

                    # start a corner
                    if x in {Pipe("F"), Pipe("L")}:
                        last_corner = x
                        continue

                    # end a corner
                    if x == Pipe("J"):
                        if last_corner == Pipe("F"):
                            status = 0 - status
                        last_corner = x
                        continue
                    if x == Pipe("7"):
                        if last_corner == Pipe("L"):
                            status = 0 - status
                        last_corner = x
                        continue

                    continue

                new_row.append(status)

            res.append(new_row)

        return numpy.asarray(res)


def go():
    data_list = list()

    from DataSample import DAY_10 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    from DataSample import DAY_10_2 as SAMPLE_2

    data_list.append(("Sample 2", SAMPLE_2))

    from DataSample import DAY_10_3 as SAMPLE_3

    data_list.append(("Sample 3", SAMPLE_3))

    try:
        from DataFull_ import DAY_10 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:

        net = Network(data.splitlines())
        start_loc = net.start[0]

        # start walking in all directions
        locs = [
            (start_loc, d)
            for d in [
                Pipe.N,
                Pipe.E,
                Pipe.W,
                Pipe.S,
            ]
        ]

        print(name)
        visited = net.walk(locs)
        pipeline = (net.pipesnp == Pipe.START) | (visited > 0)
        a = net.pipesnp
        a[numpy.invert(pipeline)] = 0
        topology = net.topology(visited)
        a[topology > 0] = -1
        print(net.print_array(a))
        print("  Farthest point:", visited.max())
        print("  Size enclosed:", (topology > 0).sum())
        print()


if __name__ == "__main__":
    go()
