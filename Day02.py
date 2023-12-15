class GameObservations:
    def __init__(self, id):
        self.id = int(id)
        self.observed = {
            "red": list(),
            "blue": list(),
            "green": list(),
        }

    def power(self):
        """
        Power = the product of max of each observed colors.
        """
        return (
            max(self.observed["red"])
            * max(self.observed["green"])
            * max(self.observed["blue"])
        )

    def observed_outcome_from_text(self, text):
        """
        Load data from text.
        """
        # split observations
        for color_info in text.split(","):
            # split color information
            color_count, color = color_info.split(None, 1)
            color_count = int(color_count)
            # look for each color
            for color_name in {"red", "green", "blue"}:
                if color_name in color:
                    # add this observaton to the list of observations
                    self.observed[color_name].append(color_count)
                    break

    def is_outcome_possible(self, red, green, blue):
        """
        Check if given outcome is possible.
        """
        return all(
            (
                red >= max(self.observed["red"]),
                green >= max(self.observed["green"]),
                blue >= max(self.observed["blue"]),
            )
        )


def load_games(data):
    games = []
    for game_str in data.splitlines():
        game_str = game_str.strip()
        if not game_str.startswith("Game"):
            continue
        game_info, data = game_str.split(":")

        game = GameObservations(game_info.split(" ")[-1])
        for game_observation in data.split(";"):
            game.observed_outcome_from_text(game_observation)

        games.append(game)

    return games


def go():
    data_list = list()

    from DataSample import DAY_2 as SAMPLE

    data_list.append(("Sample", SAMPLE))

    try:
        from DataFull_ import DAY_2 as DATA

        data_list.append(("Full Data", DATA))

    except ImportError:
        pass

    for name, data in data_list:
        print(name)

        sum_of_possible_ids = 0
        sum_of_power = 0
        games = load_games(data)

        for game in games:
            sum_of_power += game.power()
            possible = False
            if game.is_outcome_possible(red=12, green=13, blue=14):
                sum_of_possible_ids += game.id
                possible = True

            if "Sample" in name:
                print(
                    " ",
                    "Game",
                    game.id,
                    ":",
                    game.power(),
                    "Possible" if possible else "",
                )

        print("  Sum of ids of possible games: ", sum_of_possible_ids)
        print("  Sum of power of games: ", sum_of_power)
        print()


if __name__ == "__main__":
    go()
