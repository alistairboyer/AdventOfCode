class Location:
    __slots__ = "x", "y"

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not type(other) == Location:
            other = Location(*other)
        return Location(self.x + other.x, self.y + other.y)

    def __mul__(self, i: int):
        return Location(self.x * i, self.y * i)

    def __str__(self):
        return f"{self.x},{self.y}"


class Line:
    __slots__ = "start", "end", "topology", "color"

    def __init__(self, start, end, topology, color):
        self.start = start
        self.end = end
        self.topology = topology
        self.color = color

    def __str__(self):
        return f"{self.start} to {self.end} ({self.color})"

    @property
    def length(self):
        # all lines are horizontal or vertical
        return abs(self.start.x - self.end.x) + abs(self.start.y - self.end.y)

    @property
    def x_intersect_info(self):
        start, end = self.start.x, self.end.x
        if end < start:
            start, end = end, start
        return start, end, self.topology[0] == self.topology[-1]

    def svg_str(self):
        return f'<line x1="{self.start.x}" y1="{self.start.y}" x2="{self.end.x}" y2="{self.end.y}" stroke="{self.color}" stroke-linecap="round" />'


class LavaTrench:
    def __init__(self, data=None, part=1):
        self.trenches = list()
        self.caret = Location(0, 0)

        for dataline in data:
            if not dataline:
                continue
            self.add_line(dataline, part=part)
        self.close_loop_corners()

    vectors = {
        "U": Location(0, -1),
        "D": Location(0, 1),
        "L": Location(-1, 0),
        "R": Location(1, 0),
    }

    def vertices(self):
        for line in self.trenches:
            yield line.start
        yield line.end

    def svg_str(self):
        return "\n".join([line.svg_str() for line in self.trenches])

    @staticmethod
    def color_to_direction(color):
        direction = "RDLU"[int(color[-1])]
        length = int(color[1:-1], 16)
        return direction, length

    def add_line(self, linedata, part=1):
        direction, length, color = linedata.split()
        length = int(length)
        start = self.caret
        color = color.strip("(").strip(")")
        if part == 2:
            direction, length = self.color_to_direction(color)
        stop = self.caret + self.vectors[direction] * length
        topology = direction
        if self.trenches:
            topology = self.trenches[-1].topology[-1] + direction
            self.trenches[-1].topology += direction
        self.trenches.append(Line(start, stop, topology, color))
        self.caret = stop

    def close_loop_corners(self):
        first = self.trenches[0].topology[0]
        last = self.trenches[-1].topology[-1]
        self.trenches[0].topology = last + self.trenches[0].topology
        self.trenches[-1].topology += first

    def bounding_box(self):
        x_min, x_max, y_max, y_min = None, None, None, None
        for d in self.trenches:
            for val in [d.start, d.end]:
                if x_max is None or val.x > x_max:
                    x_max = val.x
                if x_min is None or val.x < x_min:
                    x_min = val.x
                if y_max is None or val.y > y_max:
                    y_max = val.y
                if y_min is None or val.y < y_min:
                    y_min = val.y
        return x_min, x_max, y_min, y_max

    def _raycast_area_ltr(self, intersects):
        # sort the intersects
        intersects.sort()

        trench_area = 0
        enclosed_area = 0

        # start off outside the area
        enclosed = False
        last_x2 = None

        for x1, x2, topology_inversion in intersects:

            # include area in trench
            trench_area += x2 - x1 + 1

            # include the area if enclosed
            if enclosed:
                enclosed_area += x1 - last_x2 - 1

            # do topology update
            if topology_inversion:
                enclosed = not enclosed

            last_x2 = x2

        if enclosed:
            raise ValueError("Loop is open along a vertical line.")

        return trench_area, enclosed_area

    def area(self):
        # initialise counters
        trench_area = 0
        enclosed_area = 0

        # Find horizontal lines
        horizontal = [line for line in self.trenches if line.start.y == line.end.y]
        horizontal.sort(key=lambda line: line.start.y)

        # take the first line
        current_horizontal = horizontal[:1]
        current_vertical = set()
        last_y = None
        # and add a dummy line to process the buffer
        for line in horizontal[1:] + [
            Line(Location(None, None), Location(None, None), "-#!", None)
        ]:

            # gather all the horizontal lines on this row
            if line.start.y == current_horizontal[0].start.y:
                current_horizontal.append(line)
                continue

            # area since last line
            vertical_intersects = [(x, x, True) for x in current_vertical]
            if current_vertical:
                lines_between = current_horizontal[0].start.y - last_y - 1
                y_trench_area, y_enclosed_area = self._raycast_area_ltr(
                    vertical_intersects
                )
                trench_area += y_trench_area * lines_between
                enclosed_area += y_enclosed_area * lines_between

            # remove ending lines from current vertical
            for h_line in current_horizontal:
                if h_line.topology[0] == "D":
                    current_vertical.remove(h_line.start.x)
                if h_line.topology[-1] == "U":
                    current_vertical.remove(h_line.end.x)

            # area along current line
            vertical_intersects = [(x, x, True) for x in current_vertical]
            horizontal_intersects = [
                line.x_intersect_info for line in current_horizontal
            ]
            y_trench_area, y_enclosed_area = self._raycast_area_ltr(
                vertical_intersects + horizontal_intersects
            )
            trench_area += y_trench_area
            enclosed_area += y_enclosed_area

            # add starting lines to current vertical
            for h_line in current_horizontal:
                if h_line.topology[0] == "U":
                    current_vertical.add(h_line.start.x)
                if h_line.topology[-1] == "D":
                    current_vertical.add(h_line.end.x)

            # update the buffered variables
            last_y = current_horizontal[0].start.y
            current_horizontal = [line]

        if current_vertical:
            raise ValueError("Loop is open along a horizontal line.")

        return trench_area, enclosed_area


def go():
    data_list = list()

    from DataSample import DAY_18 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_18 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for (name, data) in data_list:
        print()
        print(name)
        for part in (1, 2):
            print("  Part", part)
            trench = LavaTrench(data.splitlines(), part=part)
            trench_area, enclosed_area = trench.area()
            print(
                "    Trench length",
                trench_area,
                "encloses",
                enclosed_area,
                "total",
                trench_area + enclosed_area,
            )


if __name__ == "__main__":
    go()
