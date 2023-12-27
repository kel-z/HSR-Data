import json
import os
from extractors.game_data_verbose import get_game_data_verbose
from extractors.game_data import get_game_data
from extractors.sro_key_map import get_sro_mappings


# output folder
OUTPUT_PATH = "output"


def main():
    """Generate game data from game files and write it to output folder."""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if not os.path.exists(os.path.join(OUTPUT_PATH, "min")):
        os.makedirs(os.path.join(OUTPUT_PATH, "min"))

    game_data = get_game_data(include_icons=False)
    with open(os.path.join(OUTPUT_PATH, "game_data.json"), "w") as f:
        json.dump(game_data, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "game_data.json"), "w") as f:
        json.dump(game_data, f, separators=(",", ":"), indent=None)

    game_data_with_icons = get_game_data(include_icons=True)
    with open(os.path.join(OUTPUT_PATH, "game_data_with_icons.json"), "w") as f:
        json.dump(game_data_with_icons, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "game_data_with_icons.json"), "w") as f:
        json.dump(game_data_with_icons, f, separators=(",", ":"), indent=None)

    game_data_verbose = get_game_data_verbose(include_icons=False)
    with open(os.path.join(OUTPUT_PATH, "game_data_verbose.json"), "w") as f:
        json.dump(game_data_verbose, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "game_data_verbose.json"), "w") as f:
        json.dump(game_data_verbose, f, separators=(",", ":"), indent=None)

    game_data_verbose_with_icons = get_game_data_verbose(include_icons=True)
    with open(os.path.join(OUTPUT_PATH, "game_data_verbose_with_icons.json"), "w") as f:
        json.dump(game_data_verbose_with_icons, f, indent=4)
    with open(
        os.path.join(OUTPUT_PATH, "min", "game_data_verbose_with_icons.json"), "w"
    ) as f:
        json.dump(game_data_verbose_with_icons, f, separators=(",", ":"), indent=None)

    sro_key_map = get_sro_mappings(game_data)
    with open(os.path.join(OUTPUT_PATH, "sro_key_map.json"), "w") as f:
        json.dump(sro_key_map, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "sro_key_map.json"), "w") as f:
        json.dump(sro_key_map, f, separators=(",", ":"), indent=None)

    sro_to_hsrs = get_sro_mappings(game_data, swap=True)
    with open(os.path.join(OUTPUT_PATH, "sro_to_hsrs.json"), "w") as f:
        json.dump(sro_to_hsrs, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "sro_to_hsrs.json"), "w") as f:
        json.dump(sro_to_hsrs, f, separators=(",", ":"), indent=None)


if __name__ == "__main__":
    main()
