import json
from pathlib import Path


def format_item_name(name):
  # format item namespace
  if ":" in name:
    if name.startswith("c:"):
      return name.replace("c:", "cobblemon:", 1)
    return name
  return f"minecraft:{name}"


def parse_count(count_range):
  # parse count or range into item function
  if "-" in str(count_range):
    min_val, max_val = count_range.split("-")
    return {
        "function": "minecraft:set_count",
        "count": {"min": int(min_val), "max": int(max_val)},
    }
  return {"function": "minecraft:set_count", "count": int(count_range)}


def create_entry(entry_data):
  # create single loot entry object
  name = entry_data[0]
  weight = entry_data[1] if len(entry_data) > 1 else 1
  param_three = entry_data[2] if len(entry_data) > 2 else None

  entry_type = "loot_table" if "/" in name else "item"

  item_entry = {
      "type": entry_type,
      "weight": int(weight),
  }

  if entry_type == "loot_table":
    item_entry["value"] = name
  else:
    item_entry["name"] = format_item_name(name)

  if param_three is not None:
    if isinstance(param_three, list):
      item_entry["functions"] = param_three
    else:
      item_entry["functions"] = [parse_count(param_three)]

  return item_entry


def parse_rolls(rolls_val):
  # parse rolls value or range object
  if isinstance(rolls_val, str) and "-" in rolls_val:
    min_v, max_v = rolls_val.split("-")
    return {"min": int(min_v), "max": int(max_v)}
  return int(rolls_val)


def generate_loot_tables():
  # set base directories
  base_dir = Path(__file__).parent / "../"
  input_dir = base_dir / "src" / "loot_tables"
  output_dir = base_dir / "loot_table"

  if not input_dir.exists():
    return

  output_dir.mkdir(parents=True, exist_ok=True)

  # process each json file
  for input_path in input_dir.glob("*.json"):
    src_data = json.loads(input_path.read_text(encoding="utf-8"))

    for parent_key, sub_dict in src_data.items():
      for sub_name, config in sub_dict.items():
        # normalize config to entries and rolls
        if isinstance(config, list):
          entries = [create_entry(e) for e in config]
          rolls = 1
        else:
          entries = [create_entry(e) for e in config.get("entries", [])]
          rolls = parse_rolls(config.get("rolls", 1))

        output_data = {
            "type": "minecraft:chest",
            "pools": [{"rolls": rolls, "entries": entries}],
        }

        sub_dir = output_dir / parent_key
        sub_dir.mkdir(parents=True, exist_ok=True)
        output_path = sub_dir / f"{sub_name}.json"
        output_path.write_text(
            json.dumps(output_data, indent=2), encoding="utf-8"
        )


if __name__ == "__main__":
  generate_loot_tables()