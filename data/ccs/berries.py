import os
import json

TOWN_BERRIES = {
    "viridian": [
        "Oran",
        "Persim",
        "Chesto",
        "Razz",
        "Kebia",
        "Tanga"
    ],
    "pewter": [
        "Oran",
        "Persim",
        "Aspear",
        "Bluk",
        "Wacan",
        "Chople",
        "Coba",
        "Charti",
        "Babiri",
        "Yache"
    ],
    "cerulean": [
        "Oran",
        "Persim",
        "Occa",
        "Passho",
        "Charti",
        "Payapa",
        "Roseli"
    ],
    "vermilion": [
        "Oran",
        "Persim",
        "Wepear",
        "Wacan",
        "Shuca",
        "Payapa",
        "Chilan"
    ],
    "celadon": [
        "Oran",
        "Persim",
        "Chesto",
        "Razz",
        "Kebia",
        "Tanga",
        "Rindo",
        "Chople",
        "Roseli"
    ],
    "fuchsia": [
        "Oran",
        "Persim",
        "Pecha",
        "Nanab",
        "Kebia",
        "Tanga",
        "Kasib"
    ],
    "saffron": [
        "Oran",
        "Persim",
        "Cheri",
        "Wepear",
        "Wacan",
        "Chilan" 
    ],
    "cinnabar": [
        "Oran",
        "Persim",
        "Rawst",
        "Pinap",
        "Occa",
        "Shuca",
        "Payapa",
        "Charti",
        "Haban",
        "Colbur"
    ]
}

OUTPUT_DIR = "./worldgen/processor_list"

for town, berries in TOWN_BERRIES.items():
    entries = []
    for berry in berries:
        formatted_name = f"cobblemon:{berry.strip().lower()}_berry"
        entries.append({
            "weight": 1,
            "data": {
                "Name": formatted_name,
                "Properties": {
                    "age": "5"
                }
            }
        })
        
    processor_data = {
        "processors": [
            {
                "processor_type": "lithostitched:condition",
                "random_mode": "per_piece",
                "if_true": {
                    "type": "lithostitched:all_of",
                    "conditions": [
                        {
                            "type": "lithostitched:matching_blocks",
                            "blocks": "minecraft:wheat",
                            "match_type": "input"
                        }
                    ]
                },
                "then": {
                    "processor_type": "lithostitched:set_block",
                    "state_provider": {
                        "type": "minecraft:weighted_state_provider",
                        "entries": entries
                    },
                    "preserve_state": False,
                    "random_mode": "per_piece"
                },
                "else": {
                    "processor_type": "minecraft:nop"
                }
            }
        ]
    }
    
    town_dir = os.path.join(OUTPUT_DIR, town)
    os.makedirs(town_dir, exist_ok=True)
    file_path = os.path.join(town_dir, "berry.json")
    with open(file_path, "w") as f:
        json.dump(processor_data, f, indent=4)
    print(f"Generated: {file_path}")