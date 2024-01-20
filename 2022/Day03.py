import io


def letter_score(chr):
    # get character value
    ord_chr = ord(chr)
    # lower case letter
    if bool(ord_chr & 32):
        return ord_chr - 96
    # upper case letter
    return ord_chr - 38


def go():
    data_list = list()

    from DataSample import DAY_03 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_03 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)

        total = 0
        for line in io.StringIO(data):
            # trim whitespace and newlines
            line = line.strip()

            # skip blank lines
            if not line:
                continue

            # split line by halfway (//2)
            halfway = len(line) // 2

            # get common item form intersection of sets
            for common_item in set(line[:halfway]) & set(line[halfway:]):
                break

            # update total with associated score
            total += letter_score(common_item)

            if "Sample" in name:
                print("   ", common_item, letter_score(common_item))

        print("    Part 1 total:", total)
        print()

        total = 0
        line_iter = iter(io.StringIO(data))
        for line in line_iter:
            # trim whitespace and newlines
            line = line.strip()

            # skip blank lines
            if not line:
                continue

            # iterate in chunks of three
            line1 = line
            line2 = next(line_iter).strip()
            line3 = next(line_iter).strip()

            # get common item from intersection of sets
            for common_item in set(line1) & set(line2) & set(line3):
                break

            # update total with associated score
            total += letter_score(common_item)

            if "Sample" in name:
                print("   ", common_item, letter_score(common_item))

        print("    Part 2 total:", total)
        print()


if __name__ == "__main__":
    go()
