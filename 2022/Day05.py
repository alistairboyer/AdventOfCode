import io
import collections

Command = collections.namedtuple("Command", ("count", "fr", "to"))


class BoxStack:
    def __init__(self) -> None:
        self.stacks = dict()
        self.commands = list()

    def stacks_str(self) -> str:
        """Graphical output of the box stacks."""
        # collect the output strings in an list in reverse order
        result = []
        # get the labels
        result.append("   " + "    ".join(str(x) for x in self.stacks))
        # check the bottom of each stack
        i = 0
        while True:
            # init the line
            line = " "
            # go theough every stack
            for name in self.stacks:
                try:
                    # if there is an ith value in that stack save it as the box
                    line += f" [{self.stacks[name][i]}] "
                except IndexError:
                    # otherwise (IndexError) add empty space
                    line += f"     "
            # if the whole line is blacnk then there are no more boxes
            if not line.strip():
                break
            # inc i
            i += 1
            # add the result
            result.append(line + " ")
        # join the strings in revers order
        return "\n".join(result[::-1])

    def tops(self) -> str:
        """Top box in each stack joined as str with gaps for empty stacks."""
        return "".join(s[-1] or " " for s in self.stacks.values())

    def load(self, data: str) -> None:
        """Load stack information and commandsf from a str."""
        # reset internal values
        self.__init__()
        # init itertion of text
        line_iter = iter(io.StringIO(data))
        # init stacks to gather stack info
        stacks = list()
        # iterate over input
        for line in line_iter:
            # starts with "move" -> command
            if line.startswith("move"):
                self.add_command(line)
                continue
            # otherwise add to the stack info
            stacks.append(line)
        # load the stack info
        self.load_stacks(stacks)

    def load_stacks(self, stacks: str) -> None:
        """Load str containing stack information."""
        # strip newlines and remove empty lines
        stacks = [s.strip("\n\r") for s in stacks if s.strip()]
        # initialise the stacks to an empty deque
        # using the bottom line of stacks - the labels
        self.stacks = {int(name): list() for name in stacks[-1].split()}
        # get the position in the string of the labels to load the associated stack info
        stack_pos = [(name, stacks[-1].index(str(name))) for name in self.stacks]
        # iterate over the actual stacks - start at -2 to skip the label and work from the bottom up
        for row in stacks[-2::-1]:
            # get the info for each stack
            for name, pos in stack_pos:
                # if there is something in the stack add to the class info
                if row[pos].strip():
                    self.stacks[name].append(row[pos])

    def add_command(self, command: str) -> None:
        """Convert a command str to a Command and append to command list."""
        # check actually got a command
        if not command.startswith("move"):
            return
        # add to the commands list
        # take the digit parts of the str in order
        self.commands.append(Command(*[int(x) for x in command.split() if x.isdigit()]))

    def process_commands(self, reverse_transferred_boxes: bool = False) -> None:
        """Process all stored commands."""
        for command in self.commands:
            self.process_command(
                command, reverse_transferred_boxes=reverse_transferred_boxes
            )

    def process_command(
        self, command: Command, reverse_transferred_boxes: bool = False
    ) -> None:
        """Process a command."""
        # get the boxes for transfer
        transfer = self.stacks[command.fr][-command.count :]
        # remove from from the from stack
        self.stacks[command.fr] = self.stacks[command.fr][: -command.count]
        # if required reverse order of boxes
        if reverse_transferred_boxes:
            transfer = transfer[::-1]
        # add the boxes to the to stack
        self.stacks[command.to] += transfer


def go():
    data_list = list()

    from DataSample import DAY_05 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_05 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        box_stack = BoxStack()
        box_stack.load(data)
        print(box_stack.stacks_str())
        # part 1
        box_stack.process_commands(reverse_transferred_boxes=True)
        print(box_stack.stacks_str())
        print("  CrateMover 9000 top boxes:", box_stack.tops())
        # part 2
        box_stack.load(data)
        box_stack.process_commands()
        print(box_stack.stacks_str())
        print("  CrateMover 9001 top boxes:", box_stack.tops())


if __name__ == "__main__":
    go()
