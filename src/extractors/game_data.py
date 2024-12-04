from collections import defaultdict
import json
import os
import base64
from utils.helpers import get_path_from_avatar_base_type, get_slot_from_relic_type


# game version that the output is up to date with
HSR_VERSION = "2.7"

STAR_RAIL_DATA_PATH = "src/data/repos/StarRailRes"
LIGHT_CONE = STAR_RAIL_DATA_PATH + "/index_min/en/light_cones.json"
RELIC_PIECE = STAR_RAIL_DATA_PATH + "/index_min/en/relics.json"
RELIC_SET = STAR_RAIL_DATA_PATH + "/index_min/en/relic_sets.json"
CHARACTERS = STAR_RAIL_DATA_PATH + "/index_min/en/characters.json"
EIDOLONS = STAR_RAIL_DATA_PATH + "/index_min/en/character_ranks.json"
SKILLS = STAR_RAIL_DATA_PATH + "/index_min/en/character_skills.json"


def get_game_data(include_icons: bool) -> dict:
    """Get light cone, relic, and character data from game files.

    :param include_icons: Whether to include base64-encoded mini icons in the output.
    :return: A dictionary containing light cone, relic, and character data.
    """
    if not os.path.exists(STAR_RAIL_DATA_PATH):
        raise FileNotFoundError(
            "Star Rail Data submodule not found. "
            "Please run `git submodule update --init --recursive --remote`."
        )

    light_cones = get_light_cones()
    relics = get_relics()
    characters = get_characters()

    res = {
        "version": HSR_VERSION,
        "light_cones": light_cones,
        "relics": relics,
        "characters": characters,
    }

    if include_icons:
        res["mini_icons"] = get_mini_icons()

        # check that all characters have a mini icon
        for k, v in characters.items():
            for variant in v.values():
                if str(variant["id"]) not in res["mini_icons"]:
                    print(f"WARN: Missing icon for character {k} ({variant["id"]})")

    return res


def get_light_cones() -> dict:
    """Get light cone data from game files.

    :return: A dictionary containing light cone data.
    """
    with open(LIGHT_CONE, "r", encoding="utf-8") as f:
        light_cones = json.load(f)

    res = {}
    for light_cone in light_cones.values():
        res[light_cone["name"]] = {
            "id": int(light_cone["id"]),
            "rarity": light_cone["rarity"],
        }

    return res


def get_relics() -> dict:
    """Get relic data from game files.

    :return: A dictionary containing relic data.
    """
    with open(RELIC_PIECE, "r", encoding="utf-8") as f:
        relic_pieces = json.load(f)
    with open(RELIC_SET, "r", encoding="utf-8") as f:
        relic_sets = json.load(f)

    res = {}
    for relic in relic_pieces.values():
        res[relic["name"]] = {
            "set_id": int(relic["set_id"]),
            "set": relic_sets[relic["set_id"]]["name"],
            "slot": get_slot_from_relic_type(relic["type"]),
        }

    return res


def get_characters() -> dict:
    """Get character data from game files.

    :param text_map_en: A dictionary mapping string hashes to English text.
    :return: A dictionary containing character data.
    """
    with open(CHARACTERS, "r", encoding="utf-8") as f:
        characters = json.load(f)
    with open(EIDOLONS, "r", encoding="utf-8") as f:
        eidolons = json.load(f)
    with open(SKILLS, "r", encoding="utf-8") as f:
        skills = json.load(f)

    res = defaultdict(dict)
    for character in characters.values():
        name = character["name"]
        char_id = character["id"]
        if name == "{NICKNAME}":
            name = "Stelle" if int(char_id) % 2 == 0 else "Caelus"

        e3 = next(
            eidolon
            for eidolon in eidolons.values()
            if eidolon["id"] == character["ranks"][2]
        )
        e5 = next(
            eidolon
            for eidolon in eidolons.values()
            if eidolon["id"] == character["ranks"][4]
        )

        res[name][get_path_from_avatar_base_type(character["path"])] = {
            "id": int(char_id),
            "e3": _parse_skill_levels(skills, e3["level_up_skills"]),
            "e5": _parse_skill_levels(skills, e5["level_up_skills"]),
        }

    return res


def get_mini_icons():
    """Get base64-encoded mini icons from game files.

    :return: A dictionary mapping character names to base64-encoded strings.
    """
    path = "src/data/mini_icons"
    image_files = os.listdir(path)
    image_dict = {}

    for name in image_files:
        if name.endswith(".png"):
            with open(os.path.join(path, name), "rb") as f:
                encoded_icon = base64.b64encode(f.read()).decode("utf-8")
            image_dict[name[:-4]] = encoded_icon

    return image_dict


def _parse_skill_levels(skills: dict, skill_add_level_dict: dict) -> dict:
    """Parse skill levels from game files.

    :param skills: A dictionary mapping skill IDs to skill data.
    :param skill_add_level_dict: A dictionary mapping skill IDs to skill level data.
    :return: A dictionary mapping skill keys to skill levels.
    """
    res = {}
    for skill in skill_add_level_dict:
        key = ""
        match skills[skill["id"]]["type"]:
            case "Normal":
                key = "basic"
            case "BPSkill":
                key = "skill"
            case "Ultra":
                key = "ult"
            case "Talent":
                key = "talent"
            case _:
                continue
        res[key] = skill["num"]

    return res
