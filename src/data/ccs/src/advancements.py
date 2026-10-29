import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
SRC_PATH = BASE_DIR / "advancements.json"
OUTPUT_DIR = BASE_DIR / ".." / "advancement"
NAMESPACE = "ccs"

def process_advancement_item(adv_id, cfg, relative_folder=Path(""), previous_adv_id=None):
    criteria = {}
    requirements = None

    # 1. Handle "any_of" OR condition shorthand
    if "any_of" in cfg:
        or_keys = []
        for idx, item in enumerate(cfg["any_of"]):
            crit_id = item.get("id", f"condition_{idx}")
            if "structure" in item:
                criteria[crit_id] = {
                    "trigger": "minecraft:location",
                    "conditions": {
                        "player": [
                        {
                            "condition": "minecraft:entity_properties",
                            "entity": "this",
                            "predicate": {
                            "location": {
                                "structures": item["structure"]
                            }
                            }
                        }
                        ]
                    }
                }
            elif "trigger" in item:
                criteria[crit_id] = {"trigger": item["trigger"]}
            or_keys.append(crit_id)
        
        requirements = [or_keys]

    # 2. Handle single "structure" shorthand
    elif "structure" in cfg:
        criteria = {
            "entered_structure": {
                "trigger": "minecraft:location",
                "conditions": {
                    "player": [
                        {
                            "condition": "minecraft:entity_properties",
                            "entity": "this",
                            "predicate": {
                            "location": {
                                "structures": cfg["structure"]
                            }
                            }
                        }
                    ]
                }
            }
        }

    # 3. Fallback to provided criteria or minecraft:impossible
    else:
        criteria = cfg.get("criteria")
        if not criteria:
            criteria = {
                "manual_trigger": {
                    "trigger": "minecraft:impossible"
                }
            }

    if not requirements:
        requirements = cfg.get("requirements", [[k] for k in criteria.keys()])

    display = {
        "announce_to_chat": cfg.get("announce_to_chat", True),
        "show_toast": cfg.get("show_toast", True),
        "hidden": cfg.get("hidden", False),
        "icon": {"id": cfg.get("icon", "cobblemon:poke_ball")},
        "title": {"text": cfg.get("title", "")},
        "description": {"text": cfg.get("desc", "")},
    }

    if "frame" in cfg:
        display["frame"] = cfg["frame"]
    if "background" in cfg:
        display["background"] = cfg["background"]

    advancement_json = {
        "criteria": criteria,
        "display": display,
        "requirements": requirements
    }

    if "rewards" in cfg:
        advancement_json["rewards"] = cfg["rewards"]

    # Handle Parent: Sibling reference (~) > Explicit parent > Auto-chain > None
    if "parent" in cfg:
        parent_val = cfg["parent"]
        if parent_val.startswith("~"):
            sibling_id = parent_val[1:]
            folder_str = str(relative_folder).replace("\\", "/")
            if folder_str and folder_str != ".":
                advancement_json["parent"] = f"{NAMESPACE}:{folder_str}/{sibling_id}"
            else:
                advancement_json["parent"] = f"{NAMESPACE}:{sibling_id}"
        else:
            advancement_json["parent"] = parent_val
    elif previous_adv_id:
        folder_str = str(relative_folder).replace("\\", "/")
        if folder_str and folder_str != ".":
            advancement_json["parent"] = f"{NAMESPACE}:{folder_str}/{previous_adv_id}"
        else:
            advancement_json["parent"] = f"{NAMESPACE}:{previous_adv_id}"

    out_path = OUTPUT_DIR / relative_folder / f"{adv_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(advancement_json, indent=2), encoding="utf-8")

def parse_node(node_dict, current_dir=Path("")):
    last_adv_id = None
    for key, value in node_dict.items():
        is_advancement = isinstance(value, dict) and any(
            k in value for k in ["title", "desc", "criteria", "icon", "frame", "parent", "rewards", "structure", "any_of"]
        )
        
        if not is_advancement and isinstance(value, dict):
            parse_node(value, current_dir / key)
        else:
            process_advancement_item(key, value, relative_folder=current_dir, previous_adv_id=last_adv_id)
            last_adv_id = key

def build_advancements():
    if not SRC_PATH.exists():
        print("Source file not found!")
        return

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = json.loads(SRC_PATH.read_text(encoding="utf-8"))
    parse_node(data, current_dir=Path(""))

    print("advancement files generated with sibling reference support!")

if __name__ == "__main__":
    build_advancements()