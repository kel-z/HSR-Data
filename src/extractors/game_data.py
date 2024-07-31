import json
import os
import base64
from utils.helpers import get_path_from_avatar_base_type, get_slot_from_relic_type


# game version that the output is up to date with
HSR_VERSION = "2.4"

# file paths as of https://github.com/Dimbreath/StarRailData/tree/6acdba3 (Oct 8, 2023)
STAR_RAIL_DATA_PATH = "src/data/repos/StarRailData"
TEXT_MAP_EN = STAR_RAIL_DATA_PATH + "/TextMap/TextMapEN.json"
LIGHT_CONE = STAR_RAIL_DATA_PATH + "/ExcelOutput/EquipmentConfig.json"
RELIC_PIECE = STAR_RAIL_DATA_PATH + "/ExcelOutput/RelicDataInfo.json"
RELIC_SET = STAR_RAIL_DATA_PATH + "/ExcelOutput/RelicSetConfig.json"
CHARACTERS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarConfig.json"
EIDOLONS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarRankConfig.json"
SKILLS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarSkillConfig.json"


def get_game_data(include_icons: bool) -> dict:
    """Get light cone, relic, and character data from game files.

    :param include_icons: Whether to include base64-encoded mini icons in the output.
    :return: A dictionary containing light cone, relic, and character data.
    """
    if not os.path.exists(TEXT_MAP_EN):
        raise FileNotFoundError(
            "Star Rail Data submodule not found. "
            "Please run `git submodule update --init --recursive --remote`."
        )
    with open(TEXT_MAP_EN, "r", encoding="utf-8") as f:
        text_map_en = json.load(f)

    light_cones = get_light_cones(text_map_en)
    relics = get_relics(text_map_en)
    characters = get_characters(text_map_en)

    res = {
        "version": HSR_VERSION,
        "light_cones": light_cones,
        "relics": relics,
        "characters": characters,
    }

    if include_icons:
        res["mini_icons"] = get_mini_icons()

        # check that all characters have a mini icon
        for name in characters:
            name = name.replace(" ", "")
            name = "".join([c for c in name if c.isalnum()])
            if name.startswith("Trailblazer"):
                for gender in ["#F", "#M"]:
                    if name + gender not in res["mini_icons"]:
                        print(f"WARN: Missing icon for character {name + gender}")
            elif name.startswith("March7th"):
                if name + "#March7th" not in res["mini_icons"]:
                    print(f"WARN: Missing icon for character {name + '#March7th'}")
            elif name not in res["mini_icons"]:
                print(f"WARN: Missing icon for character {name}")

    return res


def get_light_cones(text_map_en: dict) -> dict:
    """Get light cone data from game files.

    :param text_map_en: A dictionary mapping string hashes to English text.
    :return: A dictionary containing light cone data.
    """
    with open(LIGHT_CONE, "r", encoding="utf-8") as f:
        light_cones = json.load(f)

    res = {}
    for lc in light_cones:
        try:
            name = text_map_en[str(lc["EquipmentName"]["Hash"])]

            res[name] = {"rarity": int(lc["Rarity"][-1])}
        except KeyError as e:
            print(f"Failed to parse light cone {lc}: {e}")
            continue

    return res


def get_relics(text_map_en: dict) -> dict:
    """Get relic data from game files.

    :param text_map_en: A dictionary mapping string hashes to English text.
    :return: A dictionary containing relic data.
    """
    with open(RELIC_PIECE, "r", encoding="utf-8") as f:
        relic_pieces = json.load(f)
    with open(RELIC_SET, "r", encoding="utf-8") as f:
        relic_sets = json.load(f)

    res = {}
    for relic in relic_pieces:
        try:
            set_name = text_map_en[
                str(
                    next(
                        rset["SetName"]
                        for rset in relic_sets
                        if rset["SetID"] == relic["SetID"]
                    )["Hash"]
                )
            ]
            name = text_map_en[_get_stable_hash(relic["RelicName"])]
            res[name] = {
                "set": set_name,
                "slot": get_slot_from_relic_type(relic["Type"]),
            }

        except KeyError as e:
            print(f"Failed to parse relic set {relic}: {e}")
            continue

    return res


def get_characters(text_map_en: dict) -> dict:
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

    res = {}
    for character in characters:
        try:
            name = text_map_en[str(character["AvatarName"]["Hash"])]
            if name == "{NICKNAME}":
                name = (
                    "Trailblazer"
                    + get_path_from_avatar_base_type(
                        character["AvatarBaseType"]
                    ).split()[-1]
                )
            elif name == "March 7th":
                name = (
                    "March 7th"
                    + get_path_from_avatar_base_type(
                        character["AvatarBaseType"]
                    ).split()[-1]
                )
            e3 = next(
                eidolon
                for eidolon in eidolons
                if eidolon["RankID"] == character["RankIDList"][2]
            )
            e5 = next(
                eidolon
                for eidolon in eidolons
                if eidolon["RankID"] == character["RankIDList"][4]
            )

            res[name] = {
                "e3": _parse_skill_levels(skills, e3["SkillAddLevelList"]),
                "e5": _parse_skill_levels(skills, e5["SkillAddLevelList"]),
            }

        except KeyError as e:
            print(f"Failed to parse character {character}: {e}")
            continue

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


def _get_stable_hash(s):
    """Get a stable hash of a string.

    :param s: The string to hash.
    :return: A stable hash of the string.
    """
    hash1 = 5381
    hash2 = hash1
    max_int = 2**31 - 1  # Maximum representable positive integer in C#

    for i in range(0, len(s), 2):
        hash1 = (((hash1 << 5) + hash1) ^ ord(s[i])) & 0xFFFFFFFF
        if i < len(s) - 1:  # additional string characters available
            hash2 = (((hash2 << 5) + hash2) ^ ord(s[i + 1])) & 0xFFFFFFFF

    hash_val = (hash1 + (hash2 * 1566083941)) & 0xFFFFFFFF

    # adjust for max signed int32 value
    return str(hash_val if hash_val <= max_int else hash_val - 2**32)


def _parse_skill_levels(skills: dict, skill_add_level_dict: dict) -> dict:
    """Parse skill levels from game files.

    :param skills: A dictionary mapping skill IDs to skill data.
    :param skill_add_level_dict: A dictionary mapping skill IDs to skill level data.
    :return: A dictionary mapping skill keys to skill levels.
    """
    res = {}
    for sid in skill_add_level_dict:
        key = ""
        skill = next(s for s in skills if s["SkillID"] == int(sid))
        match skill["SkillTriggerKey"]:
            case "Skill01":
                key = "basic"
            case "Skill02":
                key = "skill"
            case "Skill03":
                key = "ult"
            case "SkillP01":
                key = "talent"
            case _:
                continue
        res[key] = skill_add_level_dict[sid]

    return res
