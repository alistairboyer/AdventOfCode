import numpy
from typing import Generator


class Rope:
    """
    Object to represent a moving rope.

    Initialise with origin poision (int, int), and tail_length (defaults to 1).

    Attributes
    ==========
        origin (numpy.ndarray): (x, y) coordinates of origin
        head (numpy.ndarray): (x, y) coordinates of head
        tails (list[numpy.ndarray]): list of (x, y) coordinates of head
        tail_history (set[numpy.ndarray]): list of (x, y) coordinates that the last tail element has visited
        DELTAS (dict(str, numpy.ndarray)): dict of numpy.ndarray deltas for each direction {'U', 'D', 'L', 'R'}
    """

    def __init__(self, origin_position=(0, 0), tail_length=1):
        self.origin = numpy.asarray(origin_position, dtype=int)
        self.head = self.origin.copy()
        self.tails = [self.origin.copy() for _ in range(tail_length)]
        self.tail_history = set((tuple(self.tails[-1]),))

    def parse_command(self, command: str):
        """Process a str command."""
        if not command:
            return
        direction, count = command.split()
        for _ in range(int(count)):
            self.move_head(self.__class__.DELTAS[direction])

    def move_head(self, delta: numpy.ndarray) -> None:
        """Move head in direction diven by delta. See DELTAS."""
        self.head += delta
        # update location of first tail
        self.tails[0] = self.update_follower(self.head, self.tails[0])
        # update location of tail
        for i in range(1, len(self.tails)):
            self.tails[i] = self.update_follower(self.tails[i - 1], self.tails[i])
        # update history
        self.tail_history.add(tuple(self.tails[-1]))

    def update_follower(
        self, lead: numpy.ndarray, follow: numpy.ndarray
    ) -> numpy.ndarray:
        """Update follower position based upon position of lead."""
        # see difference
        difference = lead - follow
        # get absolute difference
        abs_difference = numpy.abs(difference)
        # tail is one or zero step(s) away
        if numpy.abs(difference).sum() < 2:
            return follow
        # tail is diagonally one step away
        if (abs_difference == 1).all():
            return follow
        # update location of tail
        # clip max step to be one in each direction
        return follow + numpy.clip(difference, -1, 1)

    def _get_axis(self, axis: int) -> Generator[int, None, None]:
        yield self.origin[axis]
        yield self.head[axis]
        yield from [loc[axis] for loc in self.tails]

    def to_str(self) -> str:
        """str representation of rope tail history."""
        # get x coordinates
        x_values = [self.origin[0]]
        x_values += [loc[0] for loc in self.tails]
        x_values += [loc[0] for loc in self.tail_history]
        x_values += [self.head[0]]
        # get y coordinates
        y_values = [self.origin[1]]
        y_values += [loc[1] for loc in self.tails]
        y_values += [loc[1] for loc in self.tail_history]
        y_values += [self.head[1]]
        # get min
        min_x = min(x_values)
        min_y = min(y_values)
        # initialise map
        d = numpy.full((1 + max(x_values) - min_x, 1 + max(y_values) - min_y), ".")
        d[self.origin[0] - min_x, self.origin[1] - min_y] = "s"
        for x, y in self.tail_history:
            d[x - min_x, y - min_y] = "#"
        for n, (x, y) in enumerate(self.tails):
            d[x - min_x, y - min_y] = str(n + 1)
        d[self.head[0] - min_x, self.head[1] - min_y] = "H"
        return "\n".join("".join(row) for row in d)

    DELTAS = {
        "U": numpy.asarray((-1, 0), dtype="int8"),
        "D": numpy.asarray((1, 0), dtype="int8"),
        "L": numpy.asarray((0, -1), dtype="int8"),
        "R": numpy.asarray((0, 1), dtype="int8"),
    }


def go():
    data_list = list()

    from DataSample import DAY_09 as SAMPLE
    from DataSample import DAY_09A as SAMPLEA

    data_list.append(("Sample", SAMPLE))
    data_list.append(("Sample A", SAMPLEA))
    try:
        from DataFull_ import DAY_09 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)

        rope = Rope()
        for command in data.splitlines():
            rope.parse_command(command)
        if "Sample" in name:
            print(rope.to_str())
        print(
            "The end of the rope with length 2 visited",
            len(rope.tail_history),
            "spaces.",
        )
        print()

        rope = Rope(tail_length=9)
        for command in data.splitlines():
            rope.parse_command(command)
        if "Sample" in name:
            print(rope.to_str())
        print(
            "The end of the rope with length 10 visited",
            len(rope.tail_history),
            "spaces.",
        )
        print()


if __name__ == "__main__":
    go()
