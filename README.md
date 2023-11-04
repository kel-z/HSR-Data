# HSR-Data

Contains a single formatted [JSON file](output/game_data.json) detailing Honkai: Star Rail's light cone, relic, and character metadata. Formatted specifically for [HSR-Scanner](https://github.com/kel-z/HSR-Scanner).

### Example usage:
```Python
import requests

url = "https://raw.githubusercontent.com/kel-z/HSR-Data/main/output/game_data.json"

response = requests.get(url)

# Convert the response.content to a Python dictionary
data = response.json()

# Now `data` holds the contents of game_data.json
print(data)

```

## Submodules

`src/data/repos/StarRailData` is a submodule that links to [Dimbreath/StarRailData](https://github.com/Dimbreath/StarRailData) which contains the latest game resources. The main script in this repo refers and parses the necessary files from this submodule.

## Description

[`main.py`](src/main.py) fetches the game metadata and outputs it in a structured JSON format that includes:

1. **Light Cones**: A dictionary where each key is a light cone name and the value is another dictionary with a key `rarity` whose value is the rarity of the respective light cone.

2. **Relics**: A dictionary with each key being a relic name and the value is a dictionary which holds information about the relic's `set` and `slot` values.

3. **Characters**: A dictionary where each key is a character name and the values are dictionaries that hold information about the character's eidolon level modifiers and how much `e3` or `e5` increases the character's `basic`, `skill`, `ult`, or `talent` level.

The code is structured to be run from the root directory with the `python src/main.py` command, which outputs the processed game data JSON to the `output/` directory.

## Mini icons

**Mini Icons** (optional): Images are base64 encoded and stored as strings in this dictionary, where keys are image names and values are corresponding base64 encoded image strings. These images correspond to the tiny character portrait that appears next to an item's `Equipped` tag in the inventory screen when an equipped item is selected.

However, these mini_icons must be added manually to the `src/data/mini_icons` directory, as they cannot currently be created or fetched programmatically.

## How to Generate

To generate the JSON file with the game data, perform the following steps:

1. Ensure you have Python 3.6 or newer installed
2. Clone this repository and ensure that you've also cloned the submodules properly  
   `git clone --recursive https://github.com/kel-z/HSR-Data.git`
3. Navigate to the repository's root directory in your terminal
4. Run `python src/main.py`

The resulting game data JSON will be located in the `output/` directory with the filename `game_data.json`.
