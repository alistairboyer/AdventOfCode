import collections


class Mapping:
    __slots__ = "destination", "source", "range"

    def __init__(self, destination, source=None, range=None):
        if type(destination) == Mapping:
            self.destination = destination.destination
            self.source = destination.source
            self.range = destination.range
            return

        self.destination = int(destination)
        self.source = int(source)
        self.range = int(range)
        if self.range <= 0:
            raise ValueError("Bad mapping")

    def forward(self, value):
        """
        Get by stepping forward in the mapping or return None.
        """
        if value >= self.source:
            if value < (self.source + self.range):
                delta = self.destination - self.source
                return value + delta
        return None

    def backward(self, value):
        """
        Get by stepping backward in the mapping or return None.
        """
        if value >= self.destination:
            if value < (self.destination + self.range):
                delta = self.destination - self.source
                return value - delta
        return None

    def __lt__(self, m: "Mapping"):
        return self.source < m.source

    def __str__(self):
        return f"{self.source}-{self.source+self.range} --> {self.destination}-{self.destination+self.range}"

    def is_overlapped(self, m: "Mapping"):
        """
        Check if this is overlapped the supplied mapping.
        """
        overlap_start = max(self.destination, m.destination)
        overlap_end = min(self.destination + self.range, m.destination + m.range)
        if overlap_end > overlap_start:
            return True
        overlap_start = max(self.source, m.source)
        overlap_end = min(self.source + self.range, m.source + m.range)
        if overlap_end > overlap_start:
            return True
        return False

    def merge(self, m: "Mapping"):
        """
        Try to merge a mapping checking for overlap and processing into new mappings.

        Args:
            m: Mapping
                mapping for intersection

        Returns:
            remainder: List[Mapping]
                mapping from current object remaining after operation
            overlap: Mapping
                mapping of the overlap
            merging_remainder: List[Mapping]
                mapping from merging object remaining after operation
        """

        # calculate lengths

        overlap_start = max(self.destination, m.source)
        overlap_end = min(self.destination + self.range, m.source + m.range)
        overlap_length = overlap_end - overlap_start

        # no overlap, can return early
        if overlap_length <= 0:
            return [self], None, [m]

        # initialise
        remainder = []
        overlap = None
        merging_remainder = []

        # self mapping outside overlap
        self_pre_length = overlap_start - self.destination
        self_post_length = (self.destination + self.range) - overlap_end

        # m mapping outside overlap
        m_pre_length = overlap_start - m.source
        m_post_length = (m.source + m.range) - overlap_end

        # overlapped section
        overlap = Mapping(
            m.destination + m_pre_length, self.source + self_pre_length, overlap_length
        )

        if self_pre_length > 0:
            mapping = Mapping(self.destination, self.source, self_pre_length)
            remainder.append(mapping)

        if self_post_length > 0:
            d = self.range - self_post_length
            mapping = Mapping(self.destination + d, self.source + d, self_post_length)
            remainder.append(mapping)

        if m_pre_length > 0:
            mapping = Mapping(m.destination, m.source, m_pre_length)
            merging_remainder.append(mapping)

        if m_post_length > 0:
            d = m.range - m_post_length
            mapping = Mapping(m.destination + d, m.source + d, m_post_length)
            merging_remainder.append(mapping)

        return remainder, overlap, merging_remainder


class Mappings:
    def __init__(self, name: str) -> None:
        self.name = name
        self.mappings: list["Mapping"] = list()

    def add(self, *args) -> None:
        """
        Add a new mapping to the mappings. *args passed to Mapping().
        """
        new_mapping = Mapping(*args)
        # for mapping in self.mappings:
        #    if mapping.is_overlapped(new_mapping):
        #        raise ValueError("Overlaps with existing mapping")
        self.mappings.append(new_mapping)

    def merge(self, merging: "Mappings", keep_merging_overlapped=True):
        """
        Merge another mappings with this one and create a new Mappings object.
        """

        # get the new name
        name1 = self.name.split("-")
        name2 = merging.name.split("-")
        result = Mappings(f"{name1[0]}-to-{name2[-1]}")

        merging = merging.mappings
        for mapping in self.mappings:
            complete, merging = self._merge_mapping(mapping, merging)

            # merging sections that are complete
            for m in complete:
                result.add(m)

        # merging maps that don't overlap anything else
        if keep_merging_overlapped:
            for m in merging:
                result.add(m)

        return result

    def _merge_mapping(self, current, new_mappings):
        complete = list()
        new_remaining = list()

        # create a deque containing all current mapping
        # this allows mapping to be split into parts during processing
        current_mapping = collections.deque([current])

        # go through each new mapping
        # use while and slicing to save any leftover
        while new_mappings:

            # no mapping left
            if not current_mapping:
                break

            new_map = new_mappings[0]
            new_mappings = new_mappings[1:]

            # calculate the overlap
            current_rem, overlap, new_rem = current_mapping.pop().merge(new_map)

            # save the overlap as complete
            if overlap:
                complete.append(overlap)

            # save the non overlapped parts of new mappings for later
            new_remaining += new_rem

            # add remaining current mapping back to the deque
            current_mapping += current_rem

        # save the non overlapped parts of new mappings for later
        new_remaining += new_mappings

        # save the leftover current mapping
        complete += current_mapping

        return complete, new_remaining

    def forward(self, value):
        """
        Calculate result of mapping a value.
        """
        for mapping in self.mappings:
            new_value = mapping.forward(value)
            if new_value is not None:
                return new_value
        return value

    def backward(self, value):
        """
        Calculate result of mapping a value in reverse.
        """
        for mapping in self.mappings:
            new_value = mapping.backward(value)
            if new_value is not None:
                return new_value
        return value

    def __iter__(self):
        yield from self.mappings

    def __str__(self):
        newline = "\n  "
        return f"{self.name} mapping: \n  {newline.join(str(m) for m in self.mappings)}"


def load(data_iterable, part=1):
    seeds = list()
    mappings = dict()
    for line in data_iterable:
        if line.startswith("seeds:"):
            seeds = load_seeds(line)
            continue
        if line.endswith("map:"):
            map_name = line[:-4].strip()
            mapping = Mappings(map_name)
            while line:
                try:
                    line = next(data_iterable)
                except StopIteration:
                    break
                if line:
                    mapping.add(*line.split())
            mapping.mappings.sort()
            mappings[mapping.name] = mapping
    return seeds, mappings


def load_seeds(line):
    return [int(s) for s in line[6:].split()]


ATTRIBUTES = [
    "seed",
    "soil",
    "fertilizer",
    "water",
    "light",
    "temperature",
    "humidity",
    "location",
]


def go():
    data_list = list()

    from DataSample import DAY_5 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_5

        data_list.append(("Full Data", DAY_5))

    except ImportError:
        pass

    for name, data in data_list:
        seeds, mappings = load(iter(data.splitlines()), part=1)

        # merge the mappings
        cumul_maps = list()
        for n in range(1, len(ATTRIBUTES)):
            cumul_map = mappings[f"{ATTRIBUTES[n-1]}-to-{ATTRIBUTES[n]}"]
            if cumul_maps:
                cumul_maps += [cumul_maps[-1].merge(cumul_map)]
            else:
                cumul_maps += [cumul_map]

        print(name)

        print()
        print("Part 1")
        min_location = None
        for seed_id in seeds:

            # start with
            print(f"  seed={seed_id}", end=" ")

            # get the correct mapping for the attribute
            for n in range(1, len(ATTRIBUTES)):
                map = cumul_maps[n - 1]
                attribute_id = map.forward(seed_id)
                print(f"{ATTRIBUTES[n]}={attribute_id}", end=" ")

            # calculate miniumun location
            if min_location is None:
                min_location = attribute_id
            else:
                min_location = min(attribute_id, min_location)
            print()

        print("Min location:", min_location)

        print()
        print("Part 2")

        # load the seeds as a mapping
        seed_mappings = Mappings("seed")
        for n in range(0, len(seeds), 2):
            seed_mappings.add(seeds[n], seeds[n], seeds[n + 1])

        # merge the total map from before
        # but set keep_merging_overlapped to False to only keep parts of
        # the map that lie within the seed id limits
        m = seed_mappings.merge(cumul_maps[-1], keep_merging_overlapped=False)
        # order the mappings based on destination
        m.mappings.sort(key=lambda m: m.destination)
        print(m)
        print("Min location:", m.mappings[0].destination)
        print()


if __name__ == "__main__":
    go()
