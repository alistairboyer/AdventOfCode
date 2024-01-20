import math


class Node:
    def __init__(self, tree, value, left, right) -> None:
        self.tree = tree
        self.value = value
        self.left = left
        self.right = right

    def walk_left(self):
        """
        Return node to left.
        """
        return self.tree[self.left]

    def walk_right(self):
        """
        Return node to right.
        """
        return self.tree[self.right]

    def walk(self, direction):
        """
        Return node from left or right according to direction = {L, R}.
        """
        if direction == "L":
            return self.walk_left()
        if direction == "R":
            return self.walk_right()
        raise ValueError()


class Map:
    def __init__(self, data=None):
        self.nodes = dict()
        self._step_counter = 0
        if data is not None:
            self.load(data)

    def load(self, data):
        for line in data:
            line = line.strip()
            if not line:
                continue
            if "=" not in line:
                self.steps = line
                continue
            node = Node(self, line[:3], line[7:10], line[12:15])
            self.nodes[node.value] = node

    def __getitem__(self, var):
        return self.nodes.get(var, None)

    def step_reset(self, value=0):
        """
        Reset position in step list
        """
        self._step_counter = value

    def next_step(self):
        """
        Generator for the next step direction -> {L | R}
        """
        while True:
            yield self.steps[self._step_counter]
            self._step_counter = (self._step_counter + 1) % len(self.steps)

    def walker(self, starting_point="AAA", yield_condition=lambda *a: True):
        """
        Generate a complete walk from the starting point until the yield_condition is met.
        """

        # reset counter
        self.step_reset()

        # get node as node of by text
        if type(starting_point) == Node:
            node = starting_point
        else:
            node = self[starting_point]

        # get next step
        # N.B. self.next_step() is never-ending generator
        for step_count, step in enumerate(self.next_step()):
            # take step
            node = node.walk(step)
            # check condition
            if yield_condition(node):
                yield step_count + 1, node.value, step

    def ghost_walk_iterate(self, nodes, return_condition):
        """
        Perform a complete ghost walk.
        N.B. Takes prohibitively long time for part 2!
        """

        # reset counter
        self.step_reset()

        for count, step in enumerate(self.next_step()):
            # check exit condition
            if all(return_condition(node) for node in nodes):
                return count

            nodes = [node.walk(step) for node in nodes]

    def ghost_walk_calculate(self, nodes, return_condition):
        """
        Calculate ghost walk result.
        """
        repeat_periods = []

        # consider each node spearately
        for node in nodes:

            # set up walker
            walker = self.walker(node, return_condition)
            # go through two complete cycles
            c1, val, _ = next(walker)
            c2, _, _ = next(walker)
            # check the period
            if c2 - c1 == c1:
                repeat_periods.append(c1)

        if not repeat_periods:
            return None, None

        return math.lcm(*repeat_periods), repeat_periods


def go():
    data_list = list()

    from DataSample import DAY_8 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    from DataSample import DAY_8_2 as SAMPLE2

    data_list.append(("Sample 2", SAMPLE2))

    from DataSample import DAY_8_3 as SAMPLE3

    data_list.append(("Sample 3", SAMPLE3))

    try:
        from DataFull_ import DAY_8 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    def ghost_walk_condition(node):
        return node.value[-1] == "Z"

    def walk_condition(node):
        return node.value == "ZZZ"

    for name, data in data_list:
        print(name)
        m = Map(data.splitlines())

        start_node = m["AAA"]
        if start_node:
            step_count, node_value, step = next(m.walker("AAA", walk_condition))
            print(" ", step_count, "steps from", start_node.value, "until", node_value)

        start_nodes = [node for node in m.nodes.values() if node.value.endswith("A")]
        if "Sample" in name:
            ghost_count = m.ghost_walk_iterate(start_nodes, ghost_walk_condition)
            print(" ", ghost_count, "iterated ghost steps")
            # This method is too inneficient for the full data set

        ghost_count2, ghost_periods = m.ghost_walk_calculate(
            start_nodes, ghost_walk_condition
        )
        if ghost_periods:
            print(
                " ", ghost_count2, "calculated ghost steps with period", ghost_periods
            )


if __name__ == "__main__":
    go()
