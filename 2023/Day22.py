import numpy
import collections


def alpha(n):
    ret = ""
    while n:
        # mod a number with 26 to get a letter A-Z until nothing left
        n, c = divmod(n - 1, 26)
        ret = chr(c + 65) + ret
    return ret


class Brick:
    def __init__(self, stack, data) -> None:
        self.stack = stack

        # hash and name
        self._hash = len(stack.bricks)
        self.name = alpha(self._hash + 1)

        # location
        [from_pos, to_pos] = data.split("~")
        self.from_pos = [int(x) for x in from_pos.split(",")]
        self.to_pos = [int(x) for x in to_pos.split(",")]
        self.original_from_pos = self.from_pos
        self.scale = tuple(t - f + 1 for f, t in zip(self.from_pos, self.to_pos))

        # dropped
        self.dropped = False

        # relationship info
        self.supports = set()
        self.supported_by = set()

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return self._hash

    @property
    def slice(self):
        return tuple(slice(f, t + 1) for f, t in zip(self.from_pos, self.to_pos))

    def safe_to_disintegrate(self):
        """
        True if all supported blocks have at least another block supporting them.
        """
        for supported_brick in self.supports:
            # check if this is the only brick supporting
            if supported_brick.supported_by == {self}:
                return False
        return True

    def disintegrate(self):
        """
        Number of blocks that fall if this one is removed.
        """
        disintegrated = {self}
        checklist = collections.deque([self])
        while checklist:
            brick = checklist.popleft()
            for supported_brick in brick.supports:
                # brick is supported by another
                if supported_brick.supported_by.difference(disintegrated):
                    continue
                # boom
                disintegrated.update({supported_brick})
                checklist.append(supported_brick)
        return len(disintegrated) - 1

    def drop(self):
        """
        Drop this block as low as possibel in the stack.
        """
        if self.dropped:
            return
        self.dropped = True

        # get xy cross section
        xy_footprint = tuple(
            slice(f, t + 1) for f, t in zip(self.from_pos[:2], self.to_pos[:2])
        )
        # minimum z
        min_z = min(self.from_pos[2], self.to_pos[2])

        # find next layer underneath
        layers = self.stack.stack[xy_footprint + (slice(min_z - 1, 0, -1),)]
        for n in range(layers.shape[-1]):
            layer = layers[..., n]
            if layer.any():
                break
        # nothing underneath the block - drop all the way!
        else:
            n = layers.shape[-1]
            layer = numpy.zeros(0)

        # drop by n layers
        if n:
            # print("Dropping", self.name, "by", n, "layers", end=";\t")
            self.stack.stack[self.slice] = 0
            self.from_pos = self.from_pos[:2] + [self.from_pos[2] - n]
            self.to_pos = self.to_pos[:2] + [self.to_pos[2] - n]
            self.stack.stack[self.slice] = self

        self.supported_by = set(x for x in layer.flatten() if x)
        for x in self.supported_by:
            x.supports.update({self})


class Stack:
    def __init__(self, dims) -> None:
        self.stack = numpy.zeros(dims, dtype=Brick)
        self.bricks = dict()

    def __iter__(self) -> "Brick":
        yield from self.bricks.values()

    def __getitem__(self, key) -> "Brick":
        if isinstance(key, str):
            return self.bricks[key]
        return self.stack[key]

    def add_brick(self, *data):
        """
        Add a new Brick to the stack.
        """
        brick = Brick(self, *data)
        self.stack[brick.slice] = brick
        self.bricks[brick.name] = brick

    def count_safe_to_disintegrate(self):
        """
        Count the number of blocks in the stack that can be removed without affecting others above.
        """
        return sum(brick.safe_to_disintegrate() for brick in self.bricks.values())

    def apply_gravity(self):
        """
        Move all blocks down as far as possible.
        """
        for z in range(0, self.stack.shape[2]):
            for brick in set(self.stack[..., z][numpy.nonzero(self.stack[..., z])]):
                brick.drop()


def go():
    data_list = list()

    from DataSample import DAY_22 as SAMPLE

    data_list.append(("Sample", SAMPLE, (3, 3, 15)))

    try:
        from DataFull_ import DAY_22 as DATA

        data_list.append(("Full Data", DATA, (10, 10, 310)))
    except ImportError:
        pass

    for name, data, dims in data_list:
        print(name)
        stack = Stack(dims)

        for dataline in data.splitlines():
            if not dataline:
                continue
            stack.add_brick(dataline)

        print("  Part 1")
        stack.apply_gravity()
        print(
            "   ",
            stack.count_safe_to_disintegrate(),
            "can be disintegrated without any falling.",
        )
        print("  Part 2")
        print(
            "   ",
            sum(brick.disintegrate() for brick in stack),
            "will fall if indiviual bricks are disingtegrated.",
        )
        print()


if __name__ == "__main__":
    go()
