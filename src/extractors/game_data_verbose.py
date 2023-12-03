import json
from utils.helpers import get_path_from_avatar_base_type, get_slot_from_relic_type
import urllib.parse
import os
from collections import defaultdict


# file paths as of https://github.com/Mar-7th/StarRailRes/commit/8d8f306 (Nov 14, 2023)
STAR_RAIL_RES_PATH = "src/data/repos/StarRailRes"
INFO = STAR_RAIL_RES_PATH + "/info.json"
LIGHT_CONES = STAR_RAIL_RES_PATH + "/index_new/en/light_cones.json"
LIGHT_CONE_RANKS = STAR_RAIL_RES_PATH + "/index_new/en/light_cone_ranks.json"
LIGHT_CONE_PROMOTIONS = STAR_RAIL_RES_PATH + "/index_new/en/light_cone_promotions.json"
RELICS = STAR_RAIL_RES_PATH + "/index_new/en/relics.json"
RELIC_SETS = STAR_RAIL_RES_PATH + "/index_new/en/relic_sets.json"
CHARACTERS = STAR_RAIL_RES_PATH + "/index_new/en/characters.json"
CHARACTER_SKILLS = STAR_RAIL_RES_PATH + "/index_new/en/character_skills.json"
CHARACTER_SKILL_TREES = STAR_RAIL_RES_PATH + "/index_new/en/character_skill_trees.json"
CHARACTER_RANKS = STAR_RAIL_RES_PATH + "/index_new/en/character_ranks.json"
CHARACTER_PROMOTIONS = STAR_RAIL_RES_PATH + "/index_new/en/character_promotions.json"

IMG_BASE_URL = "https://raw.githubusercontent.com/Mar-7th/StarRailRes/master/"


def get_game_data_verbose(include_icons: bool) -> dict:
    """Get light cone, relic, and character data from game files.

    :param include_icons: Whether to include icons the output.
    :return: A dictionary containing light cone, relic, and character data.
    """
    if not os.path.exists(INFO):
        raise FileNotFoundError(
            "Star Rail Res submodule not found. "
            "Please run `git submodule update --init --recursive --remote`."
        )
    with open(INFO, "r", encoding="utf-8") as f:
        INFO_JSON = json.load(f)
    VERSION = INFO_JSON["version"]

    light_cones = get_light_cones(include_icons)
    relic_sets = get_relic_sets(include_icons)
    characters = get_characters(include_icons)

    return {
        "version": VERSION,
        "light_cones": light_cones,
        "relic_sets": relic_sets,
        "characters": characters,
    }


def get_light_cones(include_icons: bool) -> dict:
    """Get light cone data from game files.

    :param include_icons: Whether to include icons in the output.
    :return: A dictionary containing light cone data.
    """
    with open(LIGHT_CONES, "r", encoding="utf-8") as f:
        LIGHT_CONE_JSON = json.load(f)
    with open(LIGHT_CONE_PROMOTIONS, "r", encoding="utf-8") as f:
        LIGHT_CONE_PROMOTIONS_JSON = json.load(f)
    with open(LIGHT_CONE_RANKS, "r", encoding="utf-8") as f:
        LIGHT_CONE_RANKS_JSON = json.load(f)

    light_cones = {}
    for key in LIGHT_CONE_JSON:
        light_cone = LIGHT_CONE_JSON[key]
        superimposition_desc, superimposition_params = _format_desc_and_params(
            LIGHT_CONE_RANKS_JSON[light_cone["id"]]["desc"],
            LIGHT_CONE_RANKS_JSON[light_cone["id"]]["params"],
        )
        light_cones[light_cone["name"]] = {
            "rarity": light_cone["rarity"],
            "path": get_path_from_avatar_base_type(light_cone["path"]),
            "desc": light_cone["desc"],
            "ascension": LIGHT_CONE_PROMOTIONS_JSON[light_cone["id"]]["values"],
            "ability": {
                "name": LIGHT_CONE_RANKS_JSON[light_cone["id"]]["skill"],
                "desc": superimposition_desc,
                "params": superimposition_params,
            },
        }
        modifiers = LIGHT_CONE_RANKS_JSON[light_cone["id"]]["properties"]
        if any(modifiers):
            light_cones[light_cone["name"]]["ability"]["modifiers"] = [
                [_format_modifier(modifier) for modifier in modifier_list]
                for modifier_list in modifiers
            ]
        if include_icons:
            light_cones[light_cone["name"]]["icon"] = (
                IMG_BASE_URL + light_cone["preview"]
            )
            light_cones[light_cone["name"]]["image"] = (
                IMG_BASE_URL + light_cone["portrait"]
            )
            light_cones[light_cone["name"]]["mini_icon"] = (
                IMG_BASE_URL + light_cone["icon"]
            )

    return light_cones


def get_relic_sets(include_icons: bool) -> dict:
    """Get relic set data from game files.

    :param include_icons: Whether to include icons in the output.
    :return: A dictionary containing relic set data.
    """
    with open(RELICS, "r", encoding="utf-8") as f:
        RELIC_JSON = json.load(f)
    with open(RELIC_SETS, "r", encoding="utf-8") as f:
        RELIC_SETS_JSON = json.load(f)

    relics = {}
    for key in RELIC_JSON:
        relic = RELIC_JSON[key]
        set_id = relic["set_id"]
        if set_id not in relics:
            relics[set_id] = {
                "pieces": defaultdict(dict),
            }
        relics[set_id]["pieces"][get_slot_from_relic_type(relic["type"])] = {
            "name": relic["name"],
        }
        if include_icons:
            relics[set_id]["pieces"][get_slot_from_relic_type(relic["type"])][
                "icon"
            ] = (IMG_BASE_URL + relic["icon"])

    relic_sets = {}
    for set_id in RELIC_SETS_JSON:
        key = RELIC_SETS_JSON[set_id]["name"]
        relic_sets[key] = relics[set_id]
        relic_sets[key]["desc"] = [
            desc for desc in RELIC_SETS_JSON[set_id]["desc"] if desc
        ]
        modifiers = RELIC_SETS_JSON[set_id]["properties"]
        if any(modifiers):
            relic_sets[key]["modifiers"] = [
                [_format_modifier(modifier) for modifier in modifier_list]
                for modifier_list in modifiers
            ]

    return relic_sets


def get_characters(include_icons: bool) -> dict:
    """Get character data from game files.

    :param include_icons: Whether to include icons in the output.
    :return: A dictionary containing character data.
    """
    with open(CHARACTERS, "r", encoding="utf-8") as f:
        CHARACTER_JSON = json.load(f)
    with open(CHARACTER_PROMOTIONS, "r", encoding="utf-8") as f:
        CHARACTER_PROMOTIONS_JSON = json.load(f)

    characters = {}
    for key in CHARACTER_JSON:
        character = CHARACTER_JSON[key]
        name = _format_name(character)
        path = get_path_from_avatar_base_type(character["path"])
        ascension = CHARACTER_PROMOTIONS_JSON[character["id"]]["values"]
        eidolons = _get_eidolons(character, include_icons)

        skills = {}
        _add_skills(skills, character, include_icons)

        traces = {}
        _add_technique_trace(traces, character, include_icons)
        _add_ability_traces(traces, character, include_icons)
        _add_passive_traces(traces, character, include_icons)

        characters[name] = {
            "rarity": character["rarity"],
            "path": path,
            "element": "Lightning"
            if character["element"] == "Thunder"
            else character["element"],
            "ascension": ascension,
            "eidolons": eidolons,
            "skills": skills,
            "traces": traces,
        }

        if include_icons:
            characters[name]["icon"] = IMG_BASE_URL + character["preview"]
            characters[name]["splash"] = IMG_BASE_URL + character["portrait"]
            characters[name]["mini_icon"] = (
                "https://raw.githubusercontent.com/kel-z/HSR-Data/main/src/"
                + urllib.parse.quote(
                    f"data/mini_icons/{''.join([c for c in name if c.isalnum() or c == '#'])}.png"
                )
            )

    return characters


def _format_name(character: dict) -> str:
    """Format the character name.

    :param character: A dictionary containing character data.
    :return: The formatted character name.
    """
    name = character["name"]
    path = get_path_from_avatar_base_type(character["path"])
    if name == "{NICKNAME}":
        name = "Trailblazer" + path
        name += "#F" if "girl" in character["tag"] else "#M"
    return name


def _format_modifier(modifier: dict) -> dict:
    """Format the modifier.

    :param modifier: A dictionary containing the modifier.
    :return: The formatted modifier.
    """
    type_map = {
        "DefenceAddedRatio": "def_",
        "QuantumAddedRatio": "quantum",
        "BreakDamageAddedRatioBase": "break",
        "ImaginaryAddedRatio": "imaginary",
        "FireAddedRatio": "fire",
        "StatusProbabilityBase": "effect_hit",
        "ThunderAddedRatio": "lightning",
        "SpeedDelta": "spd",
        "SpeedAddedRatio": "spd_",
        "IceAddedRatio": "ice",
        "StatusResistanceBase": "effect_res",
        "HPAddedRatio": "hp_",
        "AttackAddedRatio": "atk_",
        "CriticalChanceBase": "crit_rate",
        "WindAddedRatio": "wind",
        "PhysicalAddedRatio": "physical",
        "CriticalDamageBase": "crit_dmg",
        "HealRatioBase": "heal",
        "SPRatioBase": "energy",
        "AllDamageTypeAddedRatio": "all_dmg",
    }
    modifier["type"] = type_map[modifier["type"]]
    return modifier


def _add_skills(traces: dict, character: dict, include_icons: bool) -> dict:
    """Add skill traces to the traces dictionary.

    :param traces: A dictionary for storing traces.
    :param character: A dictionary containing character data.
    :param include_icons: Whether to include icons in the output.
    """
    with open(CHARACTER_SKILLS, "r", encoding="utf-8") as f:
        CHARACTER_SKILLS_JSON = json.load(f)

    for skill_id in character["skills"][:4]:
        skill = CHARACTER_SKILLS_JSON[skill_id]
        skill_type = _get_skill_type_name(skill["type"])
        max_level = skill["max_level"]
        desc, params = _format_desc_and_params(skill["desc"], skill["params"])

        traces[skill_type] = {
            "name": skill["name"],
            "max_level": max_level,
            "desc": desc,
            "params": params,
        }
        if include_icons:
            traces[skill_type]["icon"] = IMG_BASE_URL + skill["icon"]


def _add_technique_trace(traces: dict, character: dict, include_icons: bool) -> dict:
    """Add technique trace to the traces dictionary.

    :param traces: A dictionary for storing traces.
    :param character: A dictionary containing character data.
    :param include_icons: Whether to include icons in the output.
    """
    with open(CHARACTER_SKILLS, "r", encoding="utf-8") as f:
        CHARACTER_SKILLS_JSON = json.load(f)

    skill_id = character["skills"][5]
    skill = CHARACTER_SKILLS_JSON[skill_id]
    params = skill["params"]
    desc = skill["desc"]
    if params:
        for i, param in enumerate(params[0]):
            desc = desc.replace(f"#{i+1}[i]%", f"{int(param * 100)}%")
            desc = desc.replace(f"#{i+1}[i]", str(param))
            k = 1
            while f"#{i+1}[f" in desc:
                desc = desc.replace(f"#{i+1}[f{k}]", f"{param:.{k}f}")
                k += 1

    traces["technique"] = {
        "name": skill["name"],
        "desc": desc,
    }
    if include_icons:
        traces["technique"]["icon"] = IMG_BASE_URL + skill["icon"]


def _add_ability_traces(traces: dict, character: dict, include_icons: bool) -> dict:
    """Add ability traces to the traces dictionary.

    :param traces: A dictionary for storing traces.
    :param character: A dictionary containing character data.
    :param include_icons: Whether to include icons in the output.
    """
    with open(CHARACTER_SKILL_TREES, "r", encoding="utf-8") as f:
        CHARACTER_SKILL_TREES_JSON = json.load(f)

    for i, skill_id in enumerate(character["skill_trees"][5:8]):
        skill = CHARACTER_SKILL_TREES_JSON[skill_id]
        params = skill["params"]
        desc = skill["desc"]
        if params:
            for j, param in enumerate(params[0]):
                desc = desc.replace(f"#{j+1}[i]%", f"{int(param * 100)}%")
                desc = desc.replace(f"#{j+1}[i]", str(param))
                k = 1
                while f"#{j+1}[f" in desc:
                    desc = desc.replace(f"#{j+1}[f{k}]", f"{param:.{k}f}")
                    k += 1

        traces[f"ability_{i+1}"] = {
            "name": skill["name"],
            "desc": desc,
        }
        if include_icons:
            traces[f"ability_{i+1}"]["icon"] = IMG_BASE_URL + skill["icon"]


def _add_passive_traces(traces: dict, character: dict, include_icons: bool) -> dict:
    """Add passive traces to the traces dictionary.

    :param traces: A dictionary for storing traces.
    :param character: A dictionary containing character data.
    :param include_icons: Whether to include icons in the output.
    """
    with open(CHARACTER_SKILL_TREES, "r", encoding="utf-8") as f:
        CHARACTER_SKILL_TREES_JSON = json.load(f)

    for i, skill_id in enumerate(character["skill_trees"][8:]):
        skill = CHARACTER_SKILL_TREES_JSON[skill_id]
        traces[f"stat_{i+1}"] = {
            "name": skill["name"],
            "desc": _parse_property(skill["levels"][0]["properties"][0]),
            "modifiers": [
                _format_modifier(modifier)
                for modifier in skill["levels"][0]["properties"]
            ],
        }
        if include_icons:
            traces[f"stat_{i+1}"]["icon"] = IMG_BASE_URL + skill["icon"]

    # need to swap order because I guessed wrong when making the scanner (I never win my 50/50s)
    if get_path_from_avatar_base_type(character["path"]) == "Erudition":
        traces["stat_3"], traces["stat_4"] = traces["stat_4"], traces["stat_3"]
        traces["stat_6"], traces["stat_7"] = traces["stat_7"], traces["stat_6"]


def _get_eidolons(character: dict, include_icons: bool) -> dict:
    """Get the eidolons of a character.

    :param character: A dictionary containing character data.
    :param include_icons: Whether to include icons in the output.
    :return: A dictionary containing the eidolons of a character.
    """
    with open(CHARACTER_RANKS, "r", encoding="utf-8") as f:
        CHARACTER_RANKS_JSON = json.load(f)
    with open(CHARACTER_SKILLS, "r", encoding="utf-8") as f:
        CHARACTER_SKILLS_JSON = json.load(f)

    ranks = []
    for rank_id in character["ranks"]:
        rank = CHARACTER_RANKS_JSON[rank_id]
        level_up_skills = {}
        if rank["level_up_skills"]:
            for skill_dict in rank["level_up_skills"]:
                skill_type = _get_skill_type_name(
                    CHARACTER_SKILLS_JSON[skill_dict["id"]]["type"]
                )
                level_up_skills[skill_type] = skill_dict["num"]

        res = {
            "name": rank["name"],
            "desc": rank["desc"],
        }
        if level_up_skills:
            res["level_up_skills"] = level_up_skills
        if include_icons:
            res["icon"] = IMG_BASE_URL + rank["icon"]
        ranks.append(res)

    return ranks


def _format_desc_and_params(desc: str, params: list) -> str:
    """Format the description and parameters of a skill.

    :param desc: The description of a skill.
    :param params: A list of parameters.
    :return: A tuple containing the formatted description and parameters.
    """
    param_len = len(params[0])
    formatted_params = [[] for _ in range(len(params))]
    curr_i = 0
    for i in range(param_len):
        if f"#{i+1}[i]%" in desc:
            if _param_doesnt_change(params, i):
                desc = desc.replace(f"#{i+1}[i]%", f"{int(params[0][i] * 100)}%")
                continue
            desc = desc.replace(f"#{i+1}[i]%", f"{{{curr_i}}}%")
            for j, param in enumerate(params):
                formatted_params[j].append(f"{int(param[i] * 100)}")
        elif f"#{i+1}[i]" in desc:
            if _param_doesnt_change(params, i):
                desc = desc.replace(f"#{i+1}[i]", str(params[0][i]))
                continue
            desc = desc.replace(f"#{i+1}[i]", f"{{{curr_i}}}")
            for j, param in enumerate(params):
                formatted_params[j].append(str(param[i]))
        else:
            unused = True
            k = 1
            while f"#{i+1}[f" in desc:
                curr = f"#{i+1}[f{k}]%"
                existed = curr in desc
                desc = desc.replace(curr, f"{{{curr_i}}}%")
                if existed and curr not in desc:
                    if _param_doesnt_change(params, i):
                        desc = desc.replace(
                            f"{{{curr_i}}}", f"{round(params[0][i] * 100, k):.{k}f}"
                        )
                        k += 1
                        continue
                    unused = False
                    for j, param in enumerate(params):
                        formatted_params[j].append(f"{round(param[i] * 100, k):.{k}f}")
                    k += 1
                    continue

                curr = f"#{i+1}[f{k}]"
                existed = curr in desc
                desc = desc.replace(curr, f"{{{curr_i}}}")
                if existed and curr not in desc:
                    if _param_doesnt_change(params, i):
                        desc = desc.replace(f"{{{curr_i}}}", f"{param[i]:.{k}f}")
                        k += 1
                        continue
                    unused = False
                    for j, param in enumerate(params):
                        formatted_params[j].append(f"{param[i]:.{k}f}")
                k += 1
            if unused:
                continue
        curr_i += 1

    return desc, formatted_params


def _param_doesnt_change(params: list, i: int) -> bool:
    """Check if a parameter doesn't change.

    :param params: A list of parameters.
    :param i: The index of the parameter to check.
    :return: Whether the parameter doesn't change.
    """
    return len(set([params[_][i] for _ in range(len(params))])) == 1


def _parse_property(property: dict) -> str:
    """Parse a property for a passive skill.

    :param property: A dictionary containing the property.
    :return: The parsed property.
    """
    value = property["value"]
    match property["type"]:
        case "DefenceAddedRatio":
            return f"DEF increases by {value * 100}%"
        case "QuantumAddedRatio":
            return f"Quantum DMG increases by {value * 100}%"
        case "BreakDamageAddedRatioBase":
            return f"Break Effect increases by {value * 100}%"
        case "ImaginaryAddedRatio":
            return f"Imaginary DMG increases by {value * 100}%"
        case "FireAddedRatio":
            return f"Fire DMG increases by {value * 100}%"
        case "StatusProbabilityBase":
            return f"Effect Hit Rate increases by {value * 100}%"
        case "ThunderAddedRatio":
            return f"Lightning DMG increases by {value * 100}%"
        case "SpeedDelta":
            return f"SPD increases by {value}"
        case "IceAddedRatio":
            return f"Ice DMG increases by {value * 100}%"
        case "StatusResistanceBase":
            return f"Effect RES resistance increases by {value * 100}%"
        case "HPAddedRatio":
            return f"HP increases by {value * 100}%"
        case "AttackAddedRatio":
            return f"ATK increases by {value * 100}%"
        case "CriticalChanceBase":
            return f"CRIT Rate increases by {value * 100}%"
        case "WindAddedRatio":
            return f"Wind DMG increases by {value * 100}%"
        case "PhysicalAddedRatio":
            return f"Physical DMG increases by {value * 100}%"
        case "CriticalDamageBase":
            return f"CRIT DMG increases by {value * 100}%"
        case _:
            return f"Unknown property: {property['type']}"


def _get_skill_type_name(skill_type: str) -> str:
    """Get the skill type name from the skill type.

    :param skill_type: The skill type.
    :raises ValueError: If the skill type is invalid.
    :return: The skill type name.
    """
    match skill_type:
        case "Normal":
            return "basic"
        case "BPSkill":
            return "skill"
        case "Ultra":
            return "ult"
        case "Talent":
            return "talent"
        case "Technique":
            return "technique"
        case _:
            raise ValueError(f"Invalid skill type: {skill_type}")
