class PartNumber:
    def __init__(self, data=None) -> None:
        self.symbols = list()
        self.partials = list()
        if data is not None:
            self.load(data)

    def validate_parials(self) -> None:
        """
        Call the validate method on all partials.
        """
        for symbol in self.symbols:
            for partial in self.partials:
                partial.validate(symbol)

    def number(self):
        """
        Calculate the sum of the part number from the partials.
        """
        return sum(int(partial.value) for partial in self.partials if partial.symbols)

    def load(self, data):
        # enumerate rows
        for row, row_content in enumerate(data):
            # empty the partial object for new row
            partial = None

            # enumerate columns
            for col, char in enumerate(row_content):

                # if a digit is encountered
                if char.isdigit():

                    # if already have a partial
                    if partial:
                        # update the value with the new digit
                        partial.append(char)
                    else:
                        # otherwise create a new one
                        partial = PartNumberPartial(char, row, col)
                    continue

                # If no digit then save any current partial number and reset
                if partial:
                    self.partials.append(partial)
                partial = None

                # "." is a None char
                if char == ".":
                    continue

                # symbol encountered
                self.symbols.append(PartNumberSymbol(char, row, col))

            # end of row, so update any partial
            if partial:
                self.partials.append(partial)

        self.validate_parials()

    def __str__(self):
        return "\n".join(str(partial) for partial in self.partials)

    def gear_ratios_sum(self):
        """
        Return sum of all gear ratios.
        """
        return sum(symbol.gear_ratio() for symbol in self.symbols)


class PartNumberSymbol:
    def __init__(self, value, row, col) -> None:
        self.value = str(value)
        self.row = int(row)
        self.col = int(col)
        self.partials = list()

    def gear_ratio(self):
        """
        If this symbol is a gear (*) and has two associated numbers,
        return their product, otherwise return 0.
        """
        if not self.value == "*":
            return 0
        if not len(self.partials) == 2:
            return 0
        return int(self.partials[0].value) * int(self.partials[1].value)

    def __str__(self) -> str:
        return f"Symbol {self.value} at {self.row}, {self.col}"

    __repr__ = __str__


class PartNumberPartial:
    def __init__(self, value, row, col) -> None:
        self.value = str(value)
        self.row = int(row)
        self.col = int(col)
        self.symbols = list()

    def append(self, digit):
        """
        Append digit to current value.
        """
        self.value += str(int(digit))

    def __str__(self) -> str:
        return f"Partial Number {self.value} at {self.row}, {self.col} with {len(self.symbols)} adjacent symbols"

    __repr__ = __str__

    def validate(self, symbol):
        """
        Appends symbol if in validation range.
        """
        # check if symbol is within range
        if not any(
            (
                self.row < symbol.row - 1,
                self.row > symbol.row + 1,
                self.col > symbol.col + 1,
                self.col < symbol.col - len(self.value),
            )
        ):
            self.symbols.append(symbol)
            symbol.partials.append(self)


def go():
    data_list = list()

    from DataSample import DAY_3 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_3 as DATA

        data_list.append(("Full Data", DATA))

    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        part_number = PartNumber(data.splitlines())
        if "Sample" in name:
            print("   ", str(part_number).replace("\n", "\n    "))
        print("  Part number sum:", part_number.number())
        print("  Gear ratio sum:", part_number.gear_ratios_sum())
        print()


if __name__ == "__main__":
    go()
