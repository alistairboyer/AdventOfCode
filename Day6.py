def start_race(button_pushed, race_time):
    # initial velocity is zero
    boat_velocity = 0

    # push the button
    # costs race time
    race_time_remaining = max(0, race_time - button_pushed)
    # and accelerates boat    
    boat_velocity += button_pushed

    # calculate race outcome
    distance_travelled = race_time_remaining * boat_velocity
    
    return distance_travelled


def race_outcomes(race_length):
    """
    calculate all possible race outcomes for a given length.
    """
    return [start_race(button_pushed, race_length) for button_pushed in range(race_length)]


def load_data(data):
    for line in data:
        if line.startswith("Time:"):
            times = [int(t) for t in line.split()[1:]]
            continue
        if line.startswith("Distance:"):
            distances = [int(d) for d in line.split()[1:]]
            continue
    return times, distances


def go():
    # bute force method for part two but works!

    data_list = list()
    
    from DataSample import DAY_6 as SAMPLE
    data_list.append(("Part 1 Sample", SAMPLE))
    
    from DataSample import DAY_6_PART2 as SAMPLE_PART2
    data_list.append(("Part 2 Sample", SAMPLE_PART2))

    try:
        from DataFull_ import DAY_6
        data_list.append(("Full Data", DAY_6))
        from DataFull_ import DAY_6_PART2
        data_list.append(("Full Data Part 2", DAY_6_PART2))
    except ImportError:
        pass
   
    for name, data in data_list:
    
        print(name)
        times, distances = load_data(data.splitlines())
        cumulative_product = 1
        for n, (time, record) in enumerate(zip(times, distances)):
            options = race_outcomes(time)
            record_beat = [1 if o > record else 0 for o in options]
            cumulative_product *= sum(record_beat)
            print(f"  Race {n + 1}, time {time}, winning combinations {sum(record_beat)}")
        print("  Product:", cumulative_product)
        print()
  

if __name__ == "__main__":
    go()
