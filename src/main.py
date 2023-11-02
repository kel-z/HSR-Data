import base64
import json
import os

# output folder
OUTPUT_PATH = "output"

# game version that the output is up to date with
HSR_VERSION = "1.4"

# file paths as of https://github.com/Dimbreath/StarRailData/tree/6acdba3 (Oct 8, 2023)
STAR_RAIL_DATA_PATH = "src/data/repos/StarRailData"
TEXT_MAP_EN = STAR_RAIL_DATA_PATH + "/TextMap/TextMapEN.json"
LIGHT_CONE = STAR_RAIL_DATA_PATH + "/ExcelOutput/EquipmentConfig.json"
RELIC_PIECE = STAR_RAIL_DATA_PATH + "/ExcelOutput/RelicDataInfo.json"
RELIC_SET = STAR_RAIL_DATA_PATH + "/ExcelOutput/RelicSetConfig.json"
CHARACTERS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarConfig.json"
EIDOLONS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarRankConfig.json"
SKILLS = STAR_RAIL_DATA_PATH + "/ExcelOutput/AvatarSkillConfig.json"


def get_game_data(include_icons) -> dict:
    """Get light cone, relic, and character data from game files.

    :param include_icons: Whether to include base64-encoded mini icons in the output.
    :return: A dictionary containing light cone, relic, and character data.
    """
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

    return res


def get_light_cones(text_map_en: dict) -> dict:
    """Get light cone data from game files.

    :param text_map_en: A dictionary mapping string hashes to English text.
    :return: A dictionary containing light cone data.
    """
    with open(LIGHT_CONE, "r", encoding="utf-8") as f:
        light_cones = json.load(f)

    res = {}
    for lc_id in light_cones:
        try:
            lc = light_cones[lc_id]
            name = text_map_en[str(lc["EquipmentName"]["Hash"])]

            res[name] = {"rarity": int(lc["Rarity"][-1])}
        except KeyError as e:
            print(f"Failed to parse light cone {lc_id}: {e}")
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
    for rset_id in relic_pieces:
        try:
            set_name = text_map_en[str(relic_sets[rset_id]["SetName"]["Hash"])]
            relics = relic_pieces[rset_id]
            for rid in relics:
                relic = relics[rid]
                name = text_map_en[_get_stable_hash(relic["RelicName"])]
                res[name] = {
                    "setKey": set_name,
                    "slotKey": _get_slot_from_relic_type(relic["Type"]),
                }

        except KeyError as e:
            print(f"Failed to parse relic set {rset_id}: {e}")
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
    for cid in characters:
        try:
            character = characters[cid]
            name = text_map_en[str(character["AvatarName"]["Hash"])]
            if name == "{NICKNAME}":
                name = "Trailblazer" + _get_path_from_avatar_base_type(
                    character["AvatarBaseType"]
                )
            # else:
            #     name = " ".join([word for word in name.split() if word.isalnum()])

            e3_id = str(character["RankIDList"][2])
            e5_id = str(character["RankIDList"][4])

            res[name] = {
                "e3": _parse_skill_levels(skills, eidolons[e3_id]["SkillAddLevelList"]),
                "e5": _parse_skill_levels(skills, eidolons[e5_id]["SkillAddLevelList"]),
            }

        except KeyError as e:
            print(f"Failed to parse character {cid}: {e}")
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
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
                image_dict[name[:-4]] = encoded_string

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


def _get_slot_from_relic_type(relic_type: str) -> str:
    """Get the relic slot from the relic type.

    :param relic_type: The relic type.
    :raises ValueError: If the relic type is invalid.
    :return: The relic slot.
    """
    match relic_type:
        case "HEAD":
            return "Head"
        case "HAND":
            return "Hand"
        case "BODY":
            return "Body"
        case "FOOT":
            return "Foot"
        case "NECK":
            return "Link Rope"
        case "OBJECT":
            return "Planar Sphere"
        case _:
            raise ValueError(f"Invalid relic type: {relic_type}")


def _get_path_from_avatar_base_type(base_type: str) -> str:
    """Get the path from the avatar base type.

    :param base_type: The avatar base type.
    :raises ValueError: If the avatar base type is invalid.
    :return: The path.
    """
    match base_type:
        case "Warrior":
            return "Destruction"
        case "Rogue":
            return "The Hunt"
        case "Mage":
            return "Erudition"
        case "Shaman":
            return "Harmony"
        case "Warlock":
            return "Nihility"
        case "Knight":
            return "Preservation"
        case "Priest":
            return "Abundance"
        case _:
            raise ValueError(f"Invalid base type: {base_type}")


def _parse_skill_levels(skills: dict, skill_add_level_dict: dict) -> dict:
    """Parse skill levels from game files.

    :param skills: A dictionary mapping skill IDs to skill data.
    :param skill_add_level_dict: A dictionary mapping skill IDs to skill level data.
    :return: A dictionary mapping skill keys to skill levels.
    """
    res = {}

    for sid in skill_add_level_dict:
        key = ""
        match skills[sid]["1"]["SkillTriggerKey"]:
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


def main():
    """Generate game data from game files and write it to output folder."""

    if not os.path.exists(STAR_RAIL_DATA_PATH):
        raise FileNotFoundError(
            "Star Rail Data submodule not found. "
            "Please run `git submodule update --init`."
        )

    game_data = get_game_data(include_icons=False)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    with open(os.path.join(OUTPUT_PATH, "game_data.json"), "w") as f:
        json.dump(game_data, f, indent=4)

    game_data = get_game_data(include_icons=True)
    with open(os.path.join(OUTPUT_PATH, "game_data_with_icons.json"), "w") as f:
        json.dump(game_data, f, indent=4)


if __name__ == "__main__":
    main()
