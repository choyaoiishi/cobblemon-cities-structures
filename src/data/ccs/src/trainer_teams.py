import json
from pathlib import Path


def get_evo_at_stage(evo_chain, stage_index):
    # get stage evo or fall back to earlier evo
    for idx in range(stage_index, -1, -1):
        if idx < len(evo_chain) and evo_chain[idx]:
            return str(evo_chain[idx]).lower()
    return ""


def parse_trainer_file(trainer_path):
    # parse json or key value trainer file
    config = {
        "min": 0,
        "max": 0,
        "count_min": 1,
        "count_max": 6,
        "change_on": [],
        "ball": "",
        "loot": "",
        "groups": [],
    }

    if trainer_path.suffix == ".json":
        raw_data = json.loads(trainer_path.read_text(encoding="utf-8"))
        config["min"] = int(raw_data.get("min", 0))
        config["max"] = int(raw_data.get("max", 0))

        count_val = str(raw_data.get("count", "1-6"))
        if "-" in count_val:
            c_min, c_max = count_val.split("-", 1)
            config["count_min"] = int(c_min.strip())
            config["count_max"] = int(c_max.strip())
        else:
            config["count_min"] = int(count_val.strip())
            config["count_max"] = int(count_val.strip())

        change_val = raw_data.get("change_on", [])
        if isinstance(change_val, list):
            config["change_on"] = [int(x) for x in change_val]
        else:
            config["change_on"] = [int(x.strip()) for x in str(change_val).split(",") if x.strip()]

        if "ball" in raw_data and raw_data["ball"] is not None:
            config["ball"] = str(raw_data["ball"]).strip()

        if "loot" in raw_data and raw_data["loot"] is not None:
            config["loot"] = str(raw_data["loot"]).strip()

        config["groups"] = raw_data.get("groups", [])
        return config

    lines = trainer_path.read_text(encoding="utf-8").splitlines()
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            config["groups"] = json.loads(line)
        elif ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().rstrip(",").strip('"').strip("'")

            if key == "min":
                config["min"] = int(val)
            elif key == "max":
                config["max"] = int(val)
            elif key == "count":
                if "-" in val:
                    c_min, c_max = val.split("-", 1)
                    config["count_min"] = int(c_min.strip())
                    config["count_max"] = int(c_max.strip())
                else:
                    config["count_min"] = int(val)
                    config["count_max"] = int(val)
            elif key == "change_on":
                config["change_on"] = [int(x.strip()) for x in val.split(",") if x.strip()]
            elif key == "ball":
                config["ball"] = val
            elif key == "loot":
                config["loot"] = val

    return config


def format_ball_value(ball_name):
    # clean ball name without prefix
    return ball_name.strip().lower()


def format_array_block(items):
    # format items into array block
    formatted_items = ",\n".join(f"\t\t'{item}'" for item in items)
    return f"q.array(\n{formatted_items}\n\t)"


def build_molang(trainer_config, data_map):
    # build header variables
    out_lines = [
        "'generated';",
        f"v.level_variation_min = {trainer_config['min']};",
        f"v.level_variation_max = {trainer_config['max']};",
        f"v.loop_count = math.random_integer({trainer_config['count_min']}, {trainer_config['count_max']});",
    ]

    # add optional pokeball variable
    formatted_ball = format_ball_value(trainer_config.get("ball", ""))
    if formatted_ball:
        out_lines.append(f"v.pokeball = '{formatted_ball}';")

    # add optional trainer loot variable
    loot_val = str(trainer_config.get("loot", "")).strip()
    if loot_val:
        out_lines.append(f"v.trainer_loot = '{loot_val}';")

    # collect evolution chains for selected groups
    evo_chains = []
    for group in trainer_config["groups"]:
        if group in data_map and isinstance(data_map[group], list):
            for chain in data_map[group]:
                if isinstance(chain, list) and chain:
                    evo_chains.append(chain)

    thresholds = trainer_config["change_on"]

    # build stage blocks for each threshold
    for stage_idx, threshold in enumerate(thresholds):
        mons = [get_evo_at_stage(chain, stage_idx) for chain in evo_chains]
        mons = [m for m in mons if m]
        block = (
            f"v.base_level < {threshold} ? {{\n"
            f"\treturn {format_array_block(mons)};\n"
            f"}};"
        )
        out_lines.append(block)

    # build final fallback block
    final_stage_idx = len(thresholds)
    final_mons = [get_evo_at_stage(chain, final_stage_idx) for chain in evo_chains]
    final_mons = [m for m in final_mons if m]
    out_lines.append(f"return {format_array_block(final_mons)};")

    return "\n".join(out_lines) + "\n"


def load_all_data(data_dir):
    # read and lowercase all json data
    merged_data = {}
    if not data_dir.exists():
        return merged_data

    for data_path in sorted(data_dir.rglob("*.json")):
        file_data = json.loads(data_path.read_text(encoding="utf-8"))
        if isinstance(file_data, dict):
            for group_name, chains in file_data.items():
                if isinstance(chains, list):
                    clean_chains = []
                    for chain in chains:
                        if isinstance(chain, list):
                            clean_chains.append([str(mon).lower() for mon in chain if mon])
                    merged_data.setdefault(group_name, []).extend(clean_chains)

    return merged_data


def save_lowercase_data_json(data_map, data_output_dir):
    # save lowercase data json files
    data_output_dir.mkdir(parents=True, exist_ok=True)
    out_file = data_output_dir / "data.json"
    out_file.write_text(json.dumps(data_map, indent=2), encoding="utf-8")


def generate_all(src_dir, data_dir, output_dir, data_output_dir=None):
    # generate output and lowercase data json
    data_map = load_all_data(data_dir)
    if data_output_dir:
        save_lowercase_data_json(data_map, data_output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    for trainer_path in sorted(src_dir.iterdir()):
        if trainer_path.is_file() and trainer_path.suffix in {".json", ".txt"}:
            trainer_config = parse_trainer_file(trainer_path)
            molang_text = build_molang(trainer_config, data_map)
            out_file = output_dir / f"teams__{trainer_path.stem}.molang"
            out_file.write_text(molang_text, encoding="utf-8")


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "trainer_teams"
    src_folder = base_dir / "trainers"
    data_folder = base_dir / "data"
    output_folder = base_dir / ".." / ".." / "molang" / "teams" / "teams"
    data_output_folder = base_dir / "output"
    generate_all(src_folder, data_folder, output_folder, data_output_folder)