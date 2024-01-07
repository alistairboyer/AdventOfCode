import time

def go():
    performance = dict()
    for n in range(1, 26):
        start = time.perf_counter()
        try:
            exec(f"import Day{n:0>2d}")
            exec(f"Day{n:0>2d}.print = lambda *a, **k: None")
            exec(f"Day{n:0>2d}.go()")
        except Exception as e:
            continue
        stop = time.perf_counter()
        performance[n] = stop-start
        print (f"Day {n:0>2d} {performance[n]:>8.4f}")

    for n in performance:
        print (f"Day {n:0>2d} {performance[n]:>8.4f}")


if __name__ == "__main__":
    go()
 