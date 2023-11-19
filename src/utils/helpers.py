def get_slot_from_relic_type(relic_type: str) -> str:
    """Get the relic slot from the relic type.

    :param relic_type: The relic type.
    :raises ValueError: If the relic type is invalid.
    :return: The relic slot.
    """
    match relic_type:
        case "HEAD":
            return "Head"
        case "HAND":
            return "Hands"
        case "BODY":
            return "Body"
        case "FOOT":
            return "Feet"
        case "NECK":
            return "Planar Sphere"
        case "OBJECT":
            return "Link Rope"
        case _:
            raise ValueError(f"Invalid relic type: {relic_type}")


def get_path_from_avatar_base_type(base_type: str) -> str:
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
