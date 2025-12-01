import requests
import json
from tqdm import tqdm

# 1. Fetch Pokémon species names
pokemon_names = {}
for pokemon_id in tqdm(range(1, 1026), desc="Fetching Pokémon names"):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pokemon_names[pokemon_id] = data["name"]
    else:
        print(f"Failed to fetch {pokemon_id}, status {response.status_code}")

# 2. Load metadata.json
with open("metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

# 3. Update each item with the Pokémon name
for item in metadata:
    pokemon_id = metadata[item].get("id")
    if pokemon_id in pokemon_names:
        metadata[item]["name"] = pokemon_names[pokemon_id]
    else:
        metadata[item]["name"] = None  # or "" if you prefer

# 4. Save the updated metadata
with open("metadata_with_names.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("metadata.json has been updated with Pokémon names!")
