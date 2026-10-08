import os
import json

TOWN_BIOMES = {
    "pallet": [
        "minecraft:plains",
        "minecraft:meadow",
        "minecraft:sunflower_plains"
    ],
    "viridian": [
        "minecraft:forest",
        "minecraft:birch_forest",
        "minecraft:old_growth_birch_forest",
        "minecraft:flower_forest"
    ],
    "pewter": [
        "minecraft:stony_shore",
        "minecraft:windswept_gravelly_hills",
        "minecraft:stony_peaks",
        "minecraft:windswept_hills"
    ],
    "cerulean": [
        "minecraft:beach",
        "minecraft:warm_ocean",
        "minecraft:ocean",
        "minecraft:lukewarm_ocean"
    ],
    "vermilion": [
        "minecraft:savanna",
        "minecraft:savanna_plateau",
        "minecraft:windswept_savanna"
    ],
    "lavender": [
        "minecraft:dark_forest",
        "minecraft:taiga",
        "minecraft:old_growth_pine_taiga"
    ],
    "celadon": [
        "minecraft:flower_forest",
        "minecraft:meadow",
        "minecraft:cherry_grove"
    ],
    "fuchsia": [
        "minecraft:swamp",
        "minecraft:mangrove_swamp"
    ],
    "saffron": [
        "minecraft:sunflower_plains",
        "minecraft:plains",
        "minecraft:meadow"
    ],
    "cinnabar": [
        "minecraft:badlands",
        "minecraft:wooded_badlands",
        "minecraft:eroded_badlands"
    ],
    "indigo_plateau": [
        "minecraft:windswept_gravelly_hills",
        "minecraft:stony_peaks",
        "minecraft:jagged_peaks"
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