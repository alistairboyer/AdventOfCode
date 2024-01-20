from collections import OrderedDict


class Boxes:
    def __init__(self):
        self.boxes = dict()

    def remove(self, lens):
        """
        Remove lens from boxes.
        """
        box_number = HASH(lens)
        box_contents = self.boxes.get(box_number, None)
        if box_contents is None:
            return
        if lens not in box_contents:
            return
        del box_contents[lens]
        self.boxes[box_number] = box_contents

    def add(self, lens, focal_length):
        """
        Remove add lens with specified focal_length from boxes.
        """
        box_number = HASH(lens)
        box_contents = self.boxes.get(box_number, OrderedDict())
        box_contents[lens] = focal_length
        self.boxes[box_number] = box_contents

    def parse_comand(self, command):
        """
        Parse a single command.
        """
        if command[-1] == "-":
            self.remove(command[:-1])
        else:
            lens, focal_length = command.split("=")
            self.add(lens, int(focal_length))

    def power(self):
        """
        Calculate current boxes lens power.
        """
        running_total = 0
        for box_number, box in self.boxes.items():
            for slot_number, (lens, focal_length) in enumerate(box.items()):
                power = (1 + box_number) * (1 + slot_number) * focal_length
                print(
                    f"    {lens}: {box_number+1} (box {box_number}) * {slot_number+1} * {focal_length} = {power}"
                )
                running_total += power
        return running_total


def HASH(string):
    return_value = 0
    for c in string:
        # Determine the ASCII code for the current character of the string.
        # Increase the current value by the ASCII code you just determined.
        return_value += ord(c)
        # Set the current value to itself multiplied by 17.
        return_value *= 17
        # Set the current value to the remainder of dividing itself by 256.
        return_value = return_value % 256
    return return_value


def go():
    # An easy one with OrderedDicts!

    data_list = list()

    from DataSample import DAY_15 as SAMPLE
    from DataSample import DAY_15_2 as SAMPLE2

    data_list.append(("Simple Sample", SAMPLE))
    data_list.append(("Sample", SAMPLE2))

    try:
        from DataFull_ import DAY_15 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    print("Part 1")
    for name, data in data_list:
        print(" ", name)
        print("   ", data[:80])
        print("   ", sum(HASH(d) for d in data.split(",")))

    print()
    print("Part 2")
    for name, data in data_list[1:]:
        boxes = Boxes()
        print(" ", name)
        print("   ", data[:80])
        for command in data.split(","):
            boxes.parse_comand(command)
        print("  Total power", boxes.power())
        print()


if __name__ == "__main__":
    go()
