import io
import collections


def find_unique(s: str, n: int):
    """Return the index of the first occurance of n unique chars in a str; or return -1."""
    for i in range(0, len(s)-n):
        if len(set(s[i:i+n])) == n:
            return i
    return -1

def go():
    data_list = list()

    from DataSample import DAY_06 as SAMPLE
    from DataSample import DAY_06A as SAMPLEA
    from DataSample import DAY_06B as SAMPLEB
    from DataSample import DAY_06C as SAMPLEC
    from DataSample import DAY_06D as SAMPLED

    data_list.append(("Sample 1", SAMPLE))
    data_list.append(("Sample 2", SAMPLEA))
    data_list.append(("Sample 3", SAMPLEB))
    data_list.append(("Sample 4", SAMPLEC))
    data_list.append(("Sample 5", SAMPLED))

    try:
        from DataFull_ import DAY_06 as FULL_DATA

        data_list.append(("Full Data", FULL_DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name, data[:97]+'...' if len(data)>100 else data)
        print("  start @",find_unique(data, 4)+4)
        print("  message @",find_unique(data, 14)+14)


if __name__ == "__main__":
    go()

