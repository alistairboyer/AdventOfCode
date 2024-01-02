import collections
import numpy


class Machine:
    modules = dict()
    n_button_pushes = 0
    _pulses = collections.deque()
    _active_modules = collections.deque()

    def load(self, data):
        # load modules from data
        for line in data:
            self.load_module(line)
        # add an output module
        self.modules["watcher"] = Watcher(self, "output", list())
        for module in self.modules.values():
            # convert names to objects
            module.outputs = [
                self.modules.get(name, self.modules["watcher"])
                for name in module.outputs
            ]
            # update inputs
            for output_module in module.outputs:
                output_module.inputs.append(module)
            [m.reset_inputs() for m in self.modules.values()]
            self.n_button_pushes = 0

    def load_module(self, module_data):
        if not module_data:
            return
        [module, outputs] = module_data.split(" -> ")
        if module[0] == "%":
            self.modules[module[1:]] = FlipFlop(self, module[1:], outputs.split(", "))
            return
        if module[0] == "&":
            self.modules[module[1:]] = Conjunction(
                self, module[1:], outputs.split(", ")
            )
            return
        if module == "broadcaster":
            self.modules[module] = Broadcaster(self, module, outputs.split(", "))
            return

    def press_button(self):
        """
        Here at Desert Machine Headquarters, there is a module with a single
        button on it called, aptly, the button module.
        When you push the button, a single low pulse is sent directly to the broadcaster module.
        """
        self.n_button_pushes += 1
        # Send a pulse from the button to the broadcaster
        self._pulses.append(Pulse(Pulse.LOW, "button", [self.modules["broadcaster"]]))
        # Propagate all pulses until complete
        self.run()

    def run(self):
        while self._pulses or self._active_modules:
            self.step()

    def step(self):
        # deliver any pulses and activate receiving modules
        while self._pulses:
            for module in self._pulses.popleft().dispatch():
                self._active_modules.append(module)
        # process modules receiving pulses, getting new pulses
        while self._active_modules:
            module = self._active_modules.popleft()
            pulses = module.generate_pulse()

            for pulse in pulses:
                self._pulses.append(pulse)

    def flip_flop_values(self):
        return {m.name: m.value for m in self.modules.values() if type(m) == FlipFlop}


class Pulse:
    HIGH = True
    LOW = False

    total_low = 0
    total_high = 0

    def __init__(self, value, origin, destinations) -> None:
        self.value = bool(value)
        self.origin = str(origin)
        self.destinations = destinations
        if self.value:
            self.__class__.total_high += len(destinations)
        else:
            self.__class__.total_low += len(destinations)

    def __bool__(self):
        return bool(self.value)

    def __repr__(self):
        return "HIGH" if self.value else "LOW"

    @classmethod
    def counts(cls):
        return cls.total_high, cls.total_low, cls.total_low * cls.total_high

    @classmethod
    def reset_count(cls):
        cls.total_low = 0
        cls.total_high = 0

    def dispatch(self):
        for d in self.destinations:
            d.input_values[self.origin] = self
            yield d


class Module:
    def __init__(self, machine, name, outputs):
        self.machine = machine
        self.name = name
        self.outputs = outputs
        self.inputs = []
        self.period = None
        self.reset_inputs()

    def __str__(self):
        outputs_str = ", ".join(o.name for o in self.outputs)
        return f"{self.name} {type(self).__name__} module --> {outputs_str}"

    def reset_inputs(self):
        self.input_values = dict()


class FlipFlop(Module):
    """
    Flip-flop modules (prefix %) are either on (True) or off (False); they are initially off.
    If a flip-flop module receives a high pulse, it is ignored and nothing happens.
    However, if a flip-flop module receives a low pulse, it flips between on and off.
    If it was off, it turns on and sends a high pulse. If it was on, it turns off and sends a low pulse.
    """

    OFF = False
    ON = True

    def __init__(self, *args, **kwargs):
        self.value = self.OFF
        super().__init__(*args, **kwargs)

    def generate_pulse(self):
        # read and reset incoming pulse
        for pulse in self.input_values.values():
            if pulse.value == Pulse.HIGH:
                continue
            self.value = not self.value
            if self.value and self.period is None:
                self.period = self.machine.n_button_pushes
            yield Pulse(self.value, self.name, self.outputs)
        self.input_values = dict()


class Conjunction(Module):
    """
    Conjunction modules (prefix &) remember the type of the most recent pulse received from
    each of their connected input modules; they initially default to remembering a low pulse for each input.
    When a pulse is received, the conjunction module first updates its memory for that input.
    Then, if it remembers high pulses for all inputs, it sends a low pulse; otherwise, it sends a high pulse.
    """

    @property
    def value(self):
        value = Pulse.HIGH
        if all([bool(pulse) for pulse in self.input_values.values()]):
            value = Pulse.LOW
        return value

    def generate_pulse(self):
        if self.value and self.period is None:
            self.period = self.machine.n_button_pushes
        yield Pulse(self.value, self.name, self.outputs)

    def reset_inputs(self):
        self.input_values = {input.name: False for input in self.inputs}


class Broadcaster(Module):
    """
    There is a single broadcast module (named broadcaster).
    When it receives a pulse, it sends the same pulse to all of its destination modules.
    """

    @property
    def value(self):
        for pulse in self.input_values.values():
            return pulse.value

    def generate_pulse(self):
        self.input_values = dict()
        yield Pulse(self.value, self.name, self.outputs)


class Watcher(Module):
    """
    Endpoint to watch pulse sent out from a module.
    """

    BREAK_ON_LOW_PULSE = False

    @property
    def value(self):
        raise ValueError("Value not assigned.")

    def break_on_low(self):
        for pulse in self.input_values.values():
            if bool(pulse) == Pulse.LOW:
                raise StopIteration("Watcher recieved low pulse")

    def generate_pulse(self):
        if self.__class__.BREAK_ON_LOW_PULSE:
            self.break_on_low()
        self.input_values = dict()
        return []


def go():
    data_list = list()

    from DataSample import DAY_20 as SAMPLE
    from DataSample import DAY_20_2 as SAMPLE_2

    data_list.append(("Sample", SAMPLE))
    data_list.append(("Sample 2", SAMPLE_2))

    try:
        from DataFull_ import DAY_20 as DATA

        data_list.append(("Full data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print()
        print(name)

        print("  Part 1")
        Watcher.BREAK_ON_LOW_PULSE = False
        machine = Machine()
        machine.load(data.splitlines())
        for n in range(1000):
            machine.press_button()
        print(
            "    button pushed",
            n + 1,
            "times with",
            Pulse.total_high,
            "high and",
            Pulse.total_low,
            "low pulses (",
            Pulse.total_low * Pulse.total_high,
            ").",
        )

        if "Sample" in name:
            continue
        print("  Part 2")

        # raise stop iteration if the pulse is observed
        Watcher.BREAK_ON_LOW_PULSE = True

        machine = Machine()
        machine.load(data.splitlines())

        # check for period of conjunctions
        conjunctions = [
            module
            for module in machine.modules.values()
            if isinstance(module, Conjunction)
        ]
        try:
            while not all([c.period for c in conjunctions]):
                machine.press_button()
            periods = [c.period for c in conjunctions]
            print(
                "    rx activated after",
                numpy.lcm.reduce(numpy.asarray(periods, dtype="ulonglong")),
                "presses (by calculation).",
            )
        except StopIteration:
            # desired pulse objserved
            print(
                " rx activated after",
                machine.n_button_pushes,
                "presses (by observation).",
            )


if __name__ == "__main__":
    go()
