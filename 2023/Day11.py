import numpy


class Universe:
    def __init__(self, data=None) -> None:
        if data is not None:
            self.load(data)

    def load(self, data):
        data_list = list()
        for row in data:
            if not row:
                continue
            data_list.append([1 if c == "#" else 0 for c in row])
        self.data = numpy.asarray(data_list, int)

    def expand(self):
        """
        Expand the universe data by an empty set for each empty row and column.
        """
        for ax in [0, 1]:
            empty = numpy.where(self.data.sum(axis=ax) == 0)[0]
            self.data = numpy.insert(self.data, empty, 0, axis=(1 - ax))

    def step_costs(self, empty_step_size=2, step_size=1):
        """
        Return the costs for stepping in the x, y direction
        based on the default step size and step size for empty rows and columns.
        """
        # start with default step size
        x_costs = numpy.full_like(self.data[:, 0], step_size)
        # replace with empty_step_size for empty rows
        x_costs[numpy.where(self.data.sum(axis=1) == 0)[0]] = empty_step_size
        # start with default step size
        y_costs = numpy.full_like(self.data[0, :], step_size)
        # replace with empty_step_size for empty rows
        y_costs[numpy.where(self.data.sum(axis=0) == 0)[0]] = empty_step_size
        return x_costs, y_costs

    def galactic_locations(self):
        """
        Coordinates of galaxy locations.
        """
        return numpy.asarray(numpy.where(self.data)).transpose()

    def galactic_distances(self):
        """
        Calculate the total distance between all galaxies.
        """

        # initialise
        running_total = 0
        gal = self.galactic_locations()

        # duplicates symmetric matrix
        for i in range(len(gal) - 1):
            # calculate distances
            # N.B. stepped diagonal, not pythagoras
            # N.B. sum of distances
            distances = numpy.absolute(gal[i + 1 :] - gal[i]).sum(axis=1)
            running_total += distances.sum()

        return running_total

    def galactic_distances_with_cost(self, *args, **kwargs):
        """
        Calculate the total distance between all galaxies using step costs.
        args and kwargs are passed to the step_costs method.
        """

        # ititialise
        running_total = 0
        x_costs, y_costs = self.step_costs(*args, **kwargs)
        gal = self.galactic_locations()

        # duplicates symmetric matrix
        for i in range(len(gal)):
            # get location of ith galaxy
            xi, yi = gal[i]
            # distances = []
            for j in range(i + 1, len(gal)):
                distance = 0
                # get location of jth galaxy
                xj, yj = gal[j]
                # calculate x distance
                if not xi == xj:
                    # swap values if required
                    s = slice(xi, xj, 1 if xi < xj else -1)
                    # get cost by summing slice of x_costs
                    distance += x_costs[s].sum()
                # calculate y distance
                if not yi == yj:
                    # swap values if required
                    s = slice(yi, yj, 1 if yi < yj else -1)
                    # get cost by summing slice of y_costs
                    distance += y_costs[s].sum()
                # distances.append(distance)
                running_total += distance

        return running_total


def go():
    data_list = list()

    from DataSample import DAY_11 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_11 as DATA

        data_list.append(("Full Data", DATA))
    except ImportError:
        pass

    for name, data in data_list:
        print(name)
        u = Universe(data.splitlines())

        # u.expand()
        # print(u.galactic_distances())

        print(f"  {u.data.sum()} galaxies found")
        for cost in [2, 1_000_000]:
            print(
                f"  Total distances with cost {cost}:",
                u.galactic_distances_with_cost(cost),
            )

        print()


if __name__ == "__main__":
    go()
