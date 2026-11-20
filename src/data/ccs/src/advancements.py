import json
import shutil
from pathlib import Path

base_dir = Path(__file__).parent
src_path = base_dir / "advancements.json"
output_dir = base_dir / ".." / "advancement"
namespace = "ccs"


def process_advancement_item(adv_id, cfg, relative_folder=Path(""), previous_adv_id=None):
    # handle hidden record advancement without display
    if isinstance(cfg, dict) and cfg.get("hidden_record"):
        criteria_key = cfg.get("criteria_key", "impossible")
        criteria = cfg.get("criteria")
        # fall back to impossible trigger if no criteria given
        if not criteria:
            criteria = {
                criteria_key: {
                    "trigger": "minecraft:impossible"
                }
            }

        requirements = cfg.get("requirements", [[k] for k in criteria.keys()])
        advancement_json = {
            "criteria": criteria,
            "requirements": requirements,
            "sends_telemetry_event": False
        }

        if "rewards" in cfg:
            advancement_json["rewards"] = cfg["rewards"]

        if "parent" in cfg:
            advancement_json["parent"] = cfg["parent"]

        out_path = output_dir / relative_folder / f"{adv_id}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(advancement_json, indent=2), encoding="utf-8")
        return

    criteria = {}
    requirements = None

    # handle any_of or condition shorthand
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

    # handle single structure shorthand
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

    # fallback to provided criteria or impossible trigger
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

    # handle parent reference
    if "parent" in cfg:
        parent_val = cfg["parent"]
        if parent_val.startswith("~"):
            sibling_id = parent_val[1:]
            folder_str = str(relative_folder).replace("\\", "/")
            if folder_str and folder_str != ".":
                advancement_json["parent"] = f"{namespace}:{folder_str}/{sibling_id}"
            else:
                advancement_json["parent"] = f"{namespace}:{sibling_id}"
        else:
            advancement_json["parent"] = parent_val
    elif previous_adv_id:
        folder_str = str(relative_folder).replace("\\", "/")
        if folder_str and folder_str != ".":
            advancement_json["parent"] = f"{namespace}:{folder_str}/{previous_adv_id}"
        else:
            advancement_json["parent"] = f"{namespace}:{previous_adv_id}"

    out_path = output_dir / relative_folder / f"{adv_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(advancement_json, indent=2), encoding="utf-8")


def parse_node(node_dict, current_dir=Path("")):
    last_adv_id = None
    for key, value in node_dict.items():
        # check if node is an advancement or a folder
        is_advancement = isinstance(value, dict) and any(
            k in value for k in [
                "title",
                "desc",
                "criteria",
                "icon",
                "frame",
                "parent",
                "rewards",
                "structure",
                "any_of",
                "hidden_record",
            ]
        )

        if not is_advancement and isinstance(value, dict):
            parse_node(value, current_dir / key)
        else:
            process_advancement_item(key, value, relative_folder=current_dir, previous_adv_id=last_adv_id)
            last_adv_id = key


def build_advancements():
    if not src_path.exists():
        print("source file not found")
        return

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(src_path.read_text(encoding="utf-8"))
    parse_node(data, current_dir=Path(""))

    print("advancement files generated with hidden record support")


if __name__ == "__main__":
    build_advancements()