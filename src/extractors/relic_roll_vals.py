from math import ceil
import os
import json
from itertools import combinations_with_replacement
from relic_stat_vals import get_relic_stat_vals


# output folder
OUTPUT_PATH = "output"


def generate_sums(nums: list, n: int) -> list:
    """
    Generate all possible sums of given numbers up to n.

    :param nums: List of numbers.
    :param n: Maximum value.
    :return: Sorted list of all possible sums up to n.
    """
    results = []
    for i in range(1, n + 1):
        combs = combinations_with_replacement(nums, i)
        for c in combs:
            if sum(c) <= n:
                results.append(sum(c))
    return sorted(list(set(results)))


def calculate_substat_value(
    value: int, p: int, is_speed: bool, is_percentage: bool
) -> int:
    """
    Calculate substat value based on the base value and roll value.

    :param value: Base value of the substat (i.e. what 100% would be).
    :param p: Current percentage * 10. For example, 80% is 8.
    :param is_speed: Boolean indicating if it's a SPD stat.
    :param is_percentage: Boolean indicating if it's percentage
    :return: Calculated substat value.
    """
    if is_speed:
        return int(value * p / 10)
    elif is_percentage:
        return (
            ceil(value * p * 100) / 10
            if int(value * p * 10000) % 100 == 99
            else int(value * p * 100) / 10
        )
    else:
        return int(value * p / 10)


def generate_rarity_data(substat_data: dict, possible_vals: list) -> dict:
    """
    Generate data for each rarity.

    :param substat_data: Substat data.
    :param possible_vals: List of possible roll values.
    :return: Dictionary with substat data for each rarity
    """
    rarities = [2, 3, 4, 5]
    res = {}

    for rarity in rarities:
        curr_rarity = {}
        for substat, value in substat_data[rarity].items():
            curr_substat = {}
            for p in possible_vals:
                is_percentage = substat.endswith("_")
                is_speed = substat == "SPD"
                key = calculate_substat_value(value, p, is_speed, is_percentage)

                if key == 0:
                    key = 1
                elif str(key).endswith(".0"):
                    key = int(key)

                # check for overlapping roll values
                if key not in curr_substat:
                    curr_substat[key] = p / 10
                else:
                    # turn the value into an array if it's not already
                    if not isinstance(curr_substat[key], list):
                        curr_substat[key] = [curr_substat[key]]
                    curr_substat[key].append(p / 10)

            curr_rarity[substat] = curr_substat

        res[rarity] = curr_rarity

    return res


def main():
    """Generate relic stats vals from game files and write it to output folder."""
    relic_data = get_relic_stat_vals()
    possible_vals = generate_sums([8, 9, 10], 60)

    relic_roll_vals = generate_rarity_data(relic_data["sub"], possible_vals)
    with open(os.path.join(OUTPUT_PATH, "relic_roll_vals.json"), "w") as f:
        json.dump(relic_roll_vals, f, indent=4)
    with open(os.path.join(OUTPUT_PATH, "min", "relic_roll_vals.json"), "w") as f:
        json.dump(relic_roll_vals, f, separators=(",", ":"), indent=None)


if __name__ == "__main__":
    main()
