import json
import os
from collections import defaultdict


# output folder
OUTPUT_PATH = "output"

# file paths as of https://github.com/Mar-7th/StarRailRes/commit/8d8f306 (Nov 14, 2023)
STAR_RAIL_RES_PATH = "src/data/repos/StarRailRes"
RELIC_MAIN_AFFIXES = STAR_RAIL_RES_PATH + "/index_new/en/relic_main_affixes.json"
RELIC_SUB_AFFIXES = STAR_RAIL_RES_PATH + "/index_new/en/relic_sub_affixes.json"

PROPERTY_TO_MAIN = {
    "HPDelta": "HP",
    "AttackDelta": "ATK",
    "HPAddedRatio": "HP",
    "AttackAddedRatio": "ATK",
    "DefenceAddedRatio": "DEF",
    "CriticalChanceBase": "CRIT Rate",
    "CriticalDamageBase": "CRIT DMG",
    "HealRatioBase": "Outgoing Healing Boost",
    "SpeedDelta": "SPD",
    "StatusProbabilityBase": "Effect Hit Rate",
    "PhysicalAddedRatio": "Physical DMG Boost",
    "FireAddedRatio": "Fire DMG Boost",
    "IceAddedRatio": "Ice DMG Boost",
    "ThunderAddedRatio": "Lightning DMG Boost",
    "WindAddedRatio": "Wind DMG Boost",
    "QuantumAddedRatio": "Quantum DMG Boost",
    "ImaginaryAddedRatio": "Imaginary DMG Boost",
    "BreakDamageAddedRatioBase": "Break Effect",
    "SPRatioBase": "Energy Regeneration Rate",
}

PROPERTY_TO_SUB = {
    "HPDelta": "HP",
    "AttackDelta": "ATK",
    "HPAddedRatio": "HP_",
    "AttackAddedRatio": "ATK_",
    "DefenceAddedRatio": "DEF_",
    "DefenceDelta": "DEF",
    "CriticalChanceBase": "CRIT Rate_",
    "CriticalDamageBase": "CRIT DMG_",
    "SpeedDelta": "SPD",
    "StatusProbabilityBase": "Effect Hit Rate_",
    "StatusResistanceBase": "Effect RES_",
    "BreakDamageAddedRatioBase": "Break Effect_",
}


def get_relic_stat_vals():
    """Get relic stat values from game files.

    :return: A dictionary containing relic stats values.
    """
    if not os.path.exists(RELIC_MAIN_AFFIXES):
        raise FileNotFoundError(
            "Star Rail Res submodule not found. "
            "Please run `git submodule update --init --recursive --remote`."
        )
    res = {"main": _get_main_affixes(), "sub": _get_sub_affixes()}

    return res


def _get_main_affixes():
    """Get relic main affixes values from game files.

    :return: A dictionary containing relic main affixes values.
    """
    with open(RELIC_MAIN_AFFIXES, "r", encoding="utf-8") as f:
        RELIC_MAIN_AFFIXES_JSON = json.load(f)

    slots = ["Head", "Hands", "Body", "Feet", "Planar Sphere", "Link Rope"]
    rarities = [2, 3, 4, 5]
    res = {}
    for r in rarities:
        curr_rarity = {}
        for i, s in enumerate(slots):
            curr_slot = defaultdict(dict)
            curr_affixes = RELIC_MAIN_AFFIXES_JSON[f"{r}{i+1}"]["affixes"]
            for v in list(curr_affixes.values()):
                curr_slot[PROPERTY_TO_MAIN[v["property"]]]["base"] = v["base"]
                curr_slot[PROPERTY_TO_MAIN[v["property"]]]["step"] = v["step"]

            curr_rarity[s] = curr_slot
        res[r] = curr_rarity

    return res


def _get_sub_affixes():
    """Get relic sub affixes values from game files.

    :return: A dictionary containing relic sub affixes values.
    """
    with open(RELIC_SUB_AFFIXES, "r", encoding="utf-8") as f:
        RELIC_SUB_AFFIXES_JSON = json.load(f)

    rarities = [2, 3, 4, 5]
    res = {}
    for r in rarities:
        curr_rarity = {}
        curr_affixes = RELIC_SUB_AFFIXES_JSON[f"{r}"]["affixes"]
        for v in list(curr_affixes.values()):
            curr_rarity[PROPERTY_TO_SUB[v["property"]]] = v["base"] + (v["step"] * 2)

        res[r] = curr_rarity

    return res


def main():
    """Generate relic stats vals from game files and write it to output folder."""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    relic_stat_vals = get_relic_stat_vals()
    with open(os.path.join(OUTPUT_PATH, "relic_stat_vals.json"), "w") as f:
        json.dump(relic_stat_vals, f, indent=4)


if __name__ == "__main__":
    main()
