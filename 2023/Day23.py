import numpy
import collections


class WalkMap:
    def __init__(self, data) -> None:
        map_loader = list()
        for line in data:
            if not line:
                continue
            map_loader.append(list(line))

        self.map = numpy.asarray(map_loader, str)
        self._generate_point_type()
        self._find_junctions()
        self._find_paths()

    def _generate_point_type(self):
        """
        Save all the points in the map as int with a flag bit coresponding to each open direction
        """

        # initialise the data
        self.accessible_points = numpy.zeros(self.map.shape, dtype="uint8")

        # add inaccessible border for slicing
        bordered_map = numpy.pad(
            self.map, [[1, 1], [1, 1]], "constant", constant_values="#"
        )

        # set appropriate bit according to adjacent open paths
        for i, slices in [
            (MapPoint.N, (slice(0, -2), slice(1, -1))),
            (MapPoint.E, (slice(1, -1), slice(2, None))),
            (MapPoint.S, (slice(2, None), slice(1, -1))),
            (MapPoint.W, (slice(1, -1), slice(0, -2))),
        ]:
            self.accessible_points[bordered_map[slices] != "#"] |= i

        # set inaccessible points to zero
        self.accessible_points[bordered_map[1:-1, 1:-1] == "#"] = 0

        # type is the number of bits set 0 = not accessible, 1 = entry/exit, 2 = path, 3+ = junction
        self.point_type = numpy.vectorize(lambda v: bin(v).count("1"))(
            self.accessible_points
        )

    def _find_junctions(self):
        self.entryexits = list()
        self.junctions = dict()

        # find entry and exit points - special types of junction
        for (i, j) in zip(*numpy.nonzero(self.point_type == (MapPoint.ENTRYEXIT))):
            junction = Junction(
                (i, j),
                self.point_type[i, j],
                self.accessible_points[i, j],
            )
            self.entryexits.append(junction)
            self.junctions[(i, j)] = junction

        # find junctions (N.B. >= for four way junctions)
        for (i, j) in zip(*numpy.nonzero(self.point_type >= MapPoint.JUNCTION)):
            junction = Junction(
                (i, j),
                self.point_type[i, j],
                self.accessible_points[i, j],
            )
            self.junctions[(i, j)] = junction

    def _find_paths(self):
        # get a copy of the information
        paths_to_process = self.point_type.copy()
        # set all non-paths to 0
        paths_to_process[self.point_type != MapPoint.PATH] = 0
        # whilst there are any paths to consider
        while paths_to_process.any():
            # get the location of the paths using numpy.nonzero
            for location in zip(*numpy.nonzero(paths_to_process)):
                # just process the first encountered path tile
                break
            # add a path by consuming all adjacent path tiles until the end
            # update the paths_to_process to keep track
            self._add_path(location, paths_to_process)

    def _add_path(self, location, paths_to_process):
        def _follow_path(
            location, direction, blocked_forwards=False, blocked_backwards=False
        ):
            """
            Follow a path to end collecting information along the way.
            """
            while True:
                location = MapPoint.step(location, direction)
                if not paths_to_process[location]:
                    break
                paths_to_process[location] = 0
                route.append(location)
                blocked_forwards, blocked_backwards = MapPoint.flow_blocked(
                    direction, self.map[location], blocked_forwards, blocked_backwards
                )
                direction = self.accessible_points[location] - MapPoint.reverse(
                    direction
                )

            return location, blocked_forwards, blocked_backwards

        # store the route of the path
        route = [location]
        # set the process list to 0 because this location is processed
        paths_to_process[location] = 0
        # get the start of teh pah in each direction
        [backwards, forwards] = MapPoint.get_directions(
            self.accessible_points[location]
        )
        # follow the path backwards
        start, blocked_forwards, blocked_backwards = _follow_path(location, backwards)
        # flip the saved route and follow the path forwards
        route.reverse()
        end, blocked_forwards, blocked_backwards = _follow_path(
            location, forwards, blocked_backwards, blocked_forwards
        )
        # dead end
        if not self.accessible_points[start] or not self.accessible_points[end]:
            return
        # blocked both ways
        if blocked_forwards and blocked_backwards:
            return

        # create link between junctions
        path = Path(
            self.junctions[start],
            self.junctions[end],
            route,
            blocked_forwards,
            blocked_backwards,
        )
        # add link to each junction
        self.junctions[start].paths.append(path)
        self.junctions[end].paths.append(path)

    def traverse(self, from_junction, to_junction):
        if isinstance(from_junction, str):
            from_junction = self.junctions[from_junction]
        if isinstance(to_junction, str):
            to_junction = self.junctions[to_junction]

        # initialise the list of possible options
        active = collections.deque([(from_junction, 0, [])])
        max_len = 0
        # complete = list()

        while active:

            # get the route
            junction, length, visited = active.popleft()

            # arrived at finish
            if junction == to_junction:
                if length > max_len:
                    max_len = length
                    print("    New longest", length)
                    # complete.append(visited[:])
                continue

            # get next paths
            for path in junction.paths:

                next_junction, _ = path.traverse(junction)

                # blocked path
                if next_junction is None:
                    continue

                # already visisted
                if next_junction in visited:
                    continue

                # add new route option
                active.appendleft(
                    (
                        next_junction,
                        length + path.length + next_junction.length,
                        visited[:] + [junction],
                    )
                )


class MapPoint:
    INACESSIBLE = 0
    ENTRYEXIT = 1
    PATH = 2
    JUNCTION = 3
    FOUR_WAY = 4

    N = 1 << 0  # 1
    E = 1 << 1  # 2
    S = 1 << 2  # 4
    W = 1 << 3  # 8

    @classmethod
    def flow_blocked(
        cls, direction, symbol, blocked_forwards=False, blocked_backwards=False
    ):
        # no flow indication
        if symbol == ".":
            return blocked_forwards, blocked_backwards
        # check symbols for forwards
        fwd = blocked_forwards or {
            ("^", cls.N): False,
            (">", cls.E): False,
            ("v", cls.S): False,
            ("<", cls.W): False,
        }.get((symbol, direction), True)
        # check symbols for forwards
        bck = blocked_backwards or {
            (">", cls.W): False,
            ("^", cls.S): False,
            ("<", cls.E): False,
            ("v", cls.N): False,
        }.get((symbol, direction), True)
        return fwd, bck

    @classmethod
    def step(cls, location, direction):
        delta = {
            cls.N: (-1, 0),
            cls.E: (0, 1),
            cls.S: (1, 0),
            cls.W: (0, -1),
        }
        return tuple(x + dx for x, dx in zip(location, delta[direction]))

    @classmethod
    def reverse(cls, direction):
        return {
            cls.N: cls.S,
            cls.E: cls.W,
            cls.S: cls.N,
            cls.W: cls.E,
        }[direction]

    @classmethod
    def get_directions(cls, point_type):
        return [x for x in (cls.N, cls.E, cls.S, cls.W) if point_type & x]


class Junction:
    def __init__(self, location, type_number, directions):
        self.location = location
        self.type = type_number
        self.directions = directions
        self.paths = list()
        self.length = 1

    def __repr__(self):
        return f"Junction ({self.type}) at f{self.location}"


class Path:
    SLIPPY = True

    def __init__(self, start, end, route, blocked_forwards, blocked_backwards):
        self.start = start
        self.end = end
        self.route = route
        self.blocked_forwards = blocked_forwards
        self.blocked_backwards = blocked_backwards

    @property
    def length(self):
        return len(self.route)

    def traverse(self, junction):
        if junction == self.start:
            if not (self.__class__.SLIPPY and self.blocked_forwards):
                return self.end, self.route
        if junction == self.end:
            if not (self.__class__.SLIPPY and self.blocked_backwards):
                return self.start, self.route[::-1]
        return None, []


def go():
    data_list = list()

    from DataSample import DAY_23 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_23 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        wm = WalkMap(data.splitlines())
        print("  Part 1")
        Path.SLIPPY = True
        wm.traverse(*wm.entryexits)

        print("  Part 2")
        Path.SLIPPY = False
        wm.traverse(*wm.entryexits)
        print()


if __name__ == "__main__":
    go()
