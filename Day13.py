import numpy


def load(data):
    patterns = list()
    pattern = list()
    for line in data:
        if not line:
            if pattern:
                patterns.append(numpy.asarray(pattern))
            pattern = list()
            continue
        pattern.append([1 if c == "#" else 0 for c in line])
    if pattern:
        patterns.append(numpy.asarray(pattern))
    return patterns


def analyze_reflection(pattern, axis, distance=0):
    """
    Analyzes reflection along an axis, and return the location when the difference is the supplied distance.
    """
    # get shape of patten in this
    size = pattern.shape[axis]

    # enumerate over array
    for i in range(1, size):

        # get slice size = i upto half way then size-i
        slice_size = min(i, size - i)

        # different slices according to axis
        if axis == 0:
            differences = (
                pattern[i - slice_size : i, :] - pattern[i : i + slice_size, :][::-1, :]
            )
        else:
            differences = (
                pattern[:, i - slice_size : i] - pattern[:, i : i + slice_size][:, ::-1]
            )

        # check distance
        if numpy.absolute(differences).sum() == distance:
            yield i, differences


def find_reflection_h(pattern, distance=0):
    """
    Return location of a reflection in the horizontal, with specified distance using analyze_reflection.
    """
    try:
        i, _ = next(analyze_reflection(pattern, 1, distance))
        return i
    except StopIteration:
        return 0


def find_reflection_v(pattern, distance=0):
    """
    Return location of a reflection in the vertical, with specified distance using analyze_reflection.
    """
    try:
        i, _ = next(analyze_reflection(pattern, 0, distance))
        return i
    except StopIteration:
        return 0


def go():
    data_list = list()

    from DataSample import DAY_13 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_13 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        patterns = load(data.splitlines())

        reflection_code_sum = 0
        smudged_reflection_code_sum = 0

        for pattern in patterns:
            # reflections have distance 0
            reflection_h = find_reflection_h(pattern)
            reflection_v = find_reflection_v(pattern)
            reflection_code = reflection_v * 100 + reflection_h
            reflection_code_sum += reflection_code

            # smudged reflections have distance 1
            smudged_reflection_h = find_reflection_h(pattern, 1)
            smudged_reflection_v = find_reflection_v(pattern, 1)
            smudged_reflection_code = smudged_reflection_v * 100 + smudged_reflection_h
            smudged_reflection_code_sum += smudged_reflection_code

            # some nice info if it is the smaller sample
            if "Sample" in name:
                print("  Pattern")
                print("    Reflection code:", reflection_code)
                print("    Smudged reflection code:", smudged_reflection_code)

        print()
        print("  Reflection code sum:", reflection_code_sum)
        print("  Smudged reflection code sum:", smudged_reflection_code_sum)
        print()


if __name__ == "__main__":
    go()
