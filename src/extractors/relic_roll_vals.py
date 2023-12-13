from math import ceil
import os
import json
from itertools import combinations_with_replacement
import relic_stat_vals


# output folder
OUTPUT_PATH = "output"


def generate_sums(nums, n):
    """
    Generate all possible sums of given numbers up to n.

    :param nums: list of numbers
    :param n: maximum value
    :return: sorted list of all possible sums up to n
    """
    results = []
    for i in range(1, n + 1):
        combs = combinations_with_replacement(nums, i)
        for c in combs:
            if sum(c) <= n:
                results.append(sum(c))
    return sorted(list(set(results)))


def calculate_multiplier(value, p, is_speed, is_percentage):
    """
    Calculate multiplier based on several conditions.

    :param value: initial value
    :param p: possible value
    :param is_speed: boolean indicating if it's speed
    :param is_percentage: boolean indicating if it's percentage
    :return: calculated multiplier
    """
    if is_speed:
        return value * p / 10
    elif is_percentage:
        return (
            ceil(value * p * 100) / 10
            if int(value * p * 10000) % 100 == 99
            else int(value * p * 100) / 10
        )
    else:
        return value * p / 10


def generate_rarity_data(relic_data, possible_vals):
    """
    Generate data for each rarity.

    :param relic_data: initial data
    :param possible_vals: list of possible values
    :return: dictionary with data for each rarity
    """
    rarities = [2, 3, 4, 5]
    res = {}

    for rarity in rarities:
        curr_rarity = {}
        for substat, value in relic_data["sub"][str(rarity)].items():
            curr_substat = {}
            for p in possible_vals:
                is_percentage = substat.endswith("_")
                is_speed = substat == "SPD"
                multiplier = calculate_multiplier(value, p, is_speed, is_percentage)
                key = (
                    int(multiplier) if not is_percentage else int(multiplier * 10) / 10
                )

                if key == 0:
                    key = 1
                elif str(key).endswith(".0"):
                    key = int(key)

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
    if not os.path.exists(os.path.join(OUTPUT_PATH, "relic_stat_vals.json")):
        relic_stat_vals.main()

    with open(os.path.join(OUTPUT_PATH, "relic_stat_vals.json"), "r") as f:
        relic_data = json.load(f)

    possible_vals = generate_sums([8, 9, 10], 50)
    relic_roll_vals = generate_rarity_data(relic_data, possible_vals)
    with open(os.path.join(OUTPUT_PATH, "relic_roll_vals.json"), "w") as f:
        json.dump(relic_roll_vals, f, indent=4)


if __name__ == "__main__":
    main()
