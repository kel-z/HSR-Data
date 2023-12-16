import os
import json

# output folder
OUTPUT_PATH = "output"

TRAILBLAZER_MAPPINGS = {
    "TrailblazerDestruction": "TrailblazerPhysical",
    "TrailblazerPreservation": "TrailblazerFire",
}


def get_sro_mappings(game_data: dict):
    sro_key_map = {
        "characters": {},
        "relic_sets": {},
        "light_cones": {},
    }
    for name in sorted(game_data["characters"].keys()):
        if name in TRAILBLAZER_MAPPINGS:
            sro_key_map["characters"][name] = TRAILBLAZER_MAPPINGS[name]
        else:
            sro_key_map["characters"][name] = "".join(
                [
                    "".join([c for c in word.capitalize() if c.isalnum()])
                    for word in name.replace("-", " ").split()
                ]
            )

    relic_sets = set()
    for relic in game_data["relics"].values():
        relic_sets.add(relic["set"])

    for relic_set in sorted(relic_sets):
        sro_key_map["relic_sets"][relic_set] = "".join(
            [
                "".join([c for c in word.capitalize() if c.isalnum()])
                for word in relic_set.replace("-", " ").split()
            ]
        )

    for light_cone in sorted(game_data["light_cones"]):
        sro_key_map["light_cones"][light_cone] = "".join(
            [
                "".join([c for c in word.capitalize() if c.isalnum()])
                for word in light_cone.replace("-", " ").split()
            ]
        )

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


if __name__ == "__main__":
    main()
