import json
import os
from extractors.game_data_verbose import get_game_data_verbose
from extractors.game_data import get_game_data


# output folder
OUTPUT_PATH = "output"


def main():
    """Generate game data from game files and write it to output folder."""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    game_data = get_game_data(include_icons=False)
    with open(os.path.join(OUTPUT_PATH, "game_data.json"), "w") as f:
        json.dump(game_data, f, indent=4)

    game_data = get_game_data(include_icons=True)
    with open(os.path.join(OUTPUT_PATH, "game_data_with_icons.json"), "w") as f:
        json.dump(game_data, f, indent=4)

    game_data = get_game_data_verbose(include_icons=False)
    with open(os.path.join(OUTPUT_PATH, "game_data_verbose.json"), "w") as f:
        json.dump(game_data, f, indent=4)

    game_data = get_game_data_verbose(include_icons=True)
    with open(os.path.join(OUTPUT_PATH, "game_data_verbose_with_icons.json"), "w") as f:
        json.dump(game_data, f, indent=4)


if __name__ == "__main__":
    main()
