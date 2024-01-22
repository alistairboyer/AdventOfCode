import numpy


class CPU:
    """
    CPU object.

    Attributes
    ==========
        X (int): register value
        tick (int): clock ticks completed
        clock_sum (int): sum of clock * X for every clock interrrupt at 20 + every 40th tick
        crt (str): str value of the CRT
    """

    def __init__(self):
        self.X = 1
        self.clock = 0
        #
        self.clock_sum = 0
        self._crt = numpy.full((6, 40), ".")

    @property
    def crt(self) -> str:
        return "\n".join("".join(row) for row in self._crt)

    def addx(self, val) -> None:
        """Add val to X register. Takes 2 clock cycles."""
        self.tick()
        self.tick()
        self.X += val

    def noop(self) -> None:
        """Noop. Takes 1 clock cycle."""
        self.tick()

    def str_command(self, command: str) -> None:
        """Process a str command."""
        if command == "noop":
            return self.noop()
        if command.startswith("addx"):
            return self.addx(int(command.split()[-1]))

    def tick(self) -> None:
        """Calls cpu_tick and increase cpu clock by 1. Causes system clock interrupt at 20 + every 40th tick."""
        # tick the crt
        self.crt_tick()
        # increae the clock
        self.clock += 1
        # call periodic interrupt
        if self.clock >= 20 and (self.clock - 20) % 40 == 0:
            self.clock_interrupt()

    def clock_interrupt(self) -> None:
        """Periodic interrupt. Increases value of clock_sum by clock * X."""
        self.clock_sum += self.clock * self.X

    def crt_tick(self) -> None:
        # out of range -> no action
        if abs(self.clock % 40 - self.X) > 1:
            return
        self.crt_draw()

    def crt_draw(self) -> None:
        """Draw a lit pixel at the nth position in the crt."""
        # get the row and column from n
        row, col = divmod(self.clock, 40)
        # set the value
        self._crt[row, col] = "#"


def go():
    data_list = list()

    from DataSample import DAY_10 as SAMPLE

    data_list.append(("Sample", SAMPLE))
    try:
        from DataFull_ import DAY_10 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)

        cpu = CPU()
        for command in data.splitlines():
            cpu.str_command(command)
        print("  Sum of clock interrupts =", cpu.clock_sum)
        print(cpu.crt)
        print()


if __name__ == "__main__":
    go()
