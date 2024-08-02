import os
import json

# output folder
OUTPUT_PATH = "output"

ALT_PATHS_MAPPINGS = {
    "TrailblazerDestruction": "TrailblazerPhysical",
    "TrailblazerPreservation": "TrailblazerFire",
    "TrailblazerHarmony": "TrailblazerImaginary",
    "March 7thPreservation": "March7thIce",
    "March 7thHunt": "March7thImaginary",
}


def get_sro_mappings(game_data: dict, swap: bool = False):
    """Generate SRO character key mappings from game data.

    :param game_data: The game data to generate the mappings from.
    :param swap: Whether to swap the keys and values, defaults to False.
    :return: The SRO character key mappings.
    """
    sro_key_map = {
        "characters": {},
        "relic_sets": {},
        "light_cones": {},
    }
    for name in sorted(game_data["characters"].keys()):
        key = name
        value = (
            ALT_PATHS_MAPPINGS[name]
            if name in ALT_PATHS_MAPPINGS
            else "".join(
                [
                    "".join([c for c in word.capitalize() if c.isalnum()])
                    for word in name.replace("-", " ").split()
                ]
            )
        )
        if swap:
            sro_key_map["characters"][value] = key
        else:
            sro_key_map["characters"][key] = value

    relic_sets = set()
    for relic in game_data["relics"].values():
        relic_sets.add(relic["set"])

    for relic_set in sorted(relic_sets):
        key = relic_set
        value = "".join(
            [
                "".join([c for c in word.capitalize() if c.isalnum()])
                for word in relic_set.replace("-", " ").split()
            ]
        )
        if swap:
            sro_key_map["relic_sets"][value] = key
        else:
            sro_key_map["relic_sets"][key] = value

    for light_cone in sorted(game_data["light_cones"]):
        key = light_cone
        value = "".join(
            [
                "".join([c for c in word.capitalize() if c.isalnum()])
                for word in light_cone.replace("-", " ").split()
            ]
        )
        if swap:
            sro_key_map["light_cones"][value] = key
        else:
            sro_key_map["light_cones"][key] = value

    return sro_key_map


def main():
    """Generate SRO character key mappings from game files and write it to output folder."""
    if not os.path.exists(os.path.join(OUTPUT_PATH, "game_data.json")):
        print("Game data not found. Run game_data.py first.")
        return

    with open(os.path.join(OUTPUT_PATH, "game_data.json"), "r") as f:
        game_data = json.load(f)

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
