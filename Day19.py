class Part(dict):
    """
    A dict with an additional rating property that calculates the rating of the Part.
    Keys should be x, m, a, s.
    Values should all be single int values or tuples of two int representing an inclusive range.
    """

    @property
    def rating(self) -> int:
        if isinstance(self["x"], int):
            return sum(self[c] for c in "xmas")
        total = 1
        for c in "xmas":
            low, high = self[c]
            # range was wiped out
            if high < low:
                return 0
            # ranges are inclusive
            total = total * (1 + high - low)
        return total


class Workflow:
    """
    Class to execute a workflow.
    Use the from_str method to add a new process to the workflow.
    Ude the process method to process an input.
    """

    def __init__(self) -> None:
        self._workflow_single = {}
        self._workflow_range = {}

    def process(self, part, entry="in"):
        """
        Process an input throgh the workflow.
        The part should be a Part object or a dict with keys {"x", "m", "a", "s"}.
        If the values are single int values, a bool representing validity will be returned.
        If the values are tuples of two int representing an inclusive range,
        then the correponding accepted ranges will be returned.
        """
        # single part value
        if isinstance(part["x"], int):
            return self._workflow_single[entry](part)
        # part range value
        return list(self._workflow_range[entry](part))

    def from_str(self, s):
        """
        Load a process into the workflow.
        The process should be a str with the format: "xx{a<2006:yy,m>2090:A,rfg}"
        Where xx is the process name and the process information is enclosed in {}.
        The process information is comma separated values of conditions on either x, m, a, or s
        and the corresponding destination process name; "A" for accept; or "R" for reject
        if the condition is met.
        """
        # strip {} from start and end
        [name, rules] = s.strip("}").split("{")

        # creata a function represting the process for a single value
        def workflow_single(part):
            # parse rules
            for rule in rules.split(","):
                # parse rule
                rule = rule.split(":")
                endpoint = rule[-1]

                # condition
                if len(rule) == 2:
                    condition = rule[0]
                    xmas_letter = condition[0]
                    operation = condition[1]
                    number = int(condition[2:])

                    if not {">": int.__gt__, "<": int.__lt__}[operation](
                        part[xmas_letter], number
                    ):
                        continue

                # proceed to endpoints
                if endpoint == "A":  # ACCEPTED
                    return True
                if endpoint == "R":  # REJECTED
                    return False
                # RECURSION
                return self._workflow_single[endpoint](part)

        # create a function represting the process for a value range
        # this yields ranges that are accepted
        def workflow_range(partrange, depth=1):
            # parse rules
            for rule in rules.split(","):
                rule = rule.split(":")
                endpoint = rule[-1]

                # the whole range is the true_range if there are no conditions
                true_range = partrange.copy()

                # condition
                if len(rule) == 2:
                    condition = rule[0]
                    xmas_letter = condition[0]
                    operation = condition[1]
                    number = int(condition[2:])

                    # get the range of interest
                    (low, high) = partrange.pop(xmas_letter)

                    # split range of interest into true and false, reminds me of excel!
                    if operation == "<":
                        true_range = {xmas_letter: (low, min(high, number - 1))}
                        false_range = {xmas_letter: (max(low, number), high)}

                    elif operation == ">":
                        false_range = {xmas_letter: (low, min(high, number))}
                        true_range = {xmas_letter: (max(low, number + 1), high)}

                    # add the rest of the range back
                    true_range.update(partrange)
                    false_range.update(partrange)

                # first cycle through yields true_range
                if endpoint == "A":  # ACCEPTED
                    yield true_range
                elif endpoint == "R":  # REJECTED
                    pass
                else:  # RECURSION
                    yield from self._workflow_range[endpoint](true_range, depth + 1)

                # complete the next cycle using false_range
                partrange = false_range

        self._workflow_single[name] = workflow_single
        self._workflow_range[name] = workflow_range


def load(data):
    parts = list()
    workflow = Workflow()
    for line in data:
        if not line.strip():
            continue
        # parts
        if line.startswith("{"):
            x, m, a, s = "x", "m", "a", "s"
            parts.append(Part(eval(line.replace("=", ":"))))
            continue
        # workflows
        workflow.from_str(line)
    return parts, workflow


def go():
    data_list = list()

    from DataSample import DAY_19 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_19 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        print()

        # part 1
        print("Part 1")
        parts, workflow = load(data.splitlines())
        rating = 0
        for part in parts:
            print(part, end=" ")
            result = workflow.process(part)
            print(result)
            if result:
                rating += part.rating
        print(rating)
        print()

        # part 2
        print("Part 2")
        whole_range = {c: (1, 4000) for c in "xmas"}
        result = workflow.process(whole_range)
        print(result)
        result_rating = [Part(r).rating for r in result]
        print(sum(result_rating))
        print()


if __name__ == "__main__":
    go()
