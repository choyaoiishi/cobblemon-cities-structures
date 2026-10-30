import os
import json

TOWN_BIOMES = {
    "pallet": [
        "#cobblemon:is_plains"
    ],
     "lavender": [
            "#cobblemon:is_spooky"
        ],
    "viridian": [
        "#cobblemon:is_forest"
    ],
    "pewter": [
        "#cobblemon:is_mountain",
        "#cobblemon:is_peak"
    ],
    "cerulean": [
        "#cobblemon:is_lukewarm_and_temperate_ocean"
    ],
    "vermilion": [
        "#cobblemon:is_savanna"
    ],
    "celadon": [
        "#cobblemon:is_floral"
    ],
    "fuchsia": [
        "#cobblemon:is_swamp"
    ],
    "saffron": [
        "#cobblemon:is_plains"
    ],
    "cinnabar": [
        "#cobblemon:is_badlands"
    ]
}

OUTPUT_DIR = "./tags/worldgen/biome"

for town, biomes in TOWN_BIOMES.items():
    tag_data = {
        "replace": False,
        "values": biomes
    }
    file_path = os.path.join(OUTPUT_DIR, f"{town}.json")
    with open(file_path, "w") as f:
        json.dump(tag_data, f, indent=4)
    print(f"Generated: {file_path}")