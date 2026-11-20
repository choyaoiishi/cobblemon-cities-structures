import json
from pathlib import Path


def escape_line(line):
    # escape single quotes for molang strings
    return line.replace("'", "\\'")


def build_molang_from_trainer(trainer_path, data_dir):
    # read trainer list
    trainer_keys = json.loads(trainer_path.read_text(encoding="utf-8"))

    battle_lines = []
    win_lines = []
    won_lines = []

    for key in trainer_keys:
        data_file = data_dir / f"{key}.json"
        if not data_file.exists():
            continue

        entries = json.loads(data_file.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, list) and len(entry) >= 3:
                battle_lines.append(f"    '{escape_line(entry[0])}'")
                win_lines.append(f"    '{escape_line(entry[1])}'")
                won_lines.append(f"    '{escape_line(entry[2])}'")

    # build molang blocks
    battle_block = "v.lines__battle = q.array(\n" + ",\n".join(battle_lines) + "\n);"
    win_block = "v.lines__win = q.array(\n" + ",\n".join(win_lines) + "\n);"
    won_block = "v.lines__won = q.array(\n" + ",\n".join(won_lines) + "\n);"

    return "\n".join([battle_block, win_block, won_block]) + "\n"


def compile_all_trainers(trainers_dir, data_dir, output_dir):
    # make output folder if missing
    output_dir.mkdir(parents=True, exist_ok=True)

    for trainer_path in trainers_dir.glob("*.json"):
        molang_text = build_molang_from_trainer(trainer_path, data_dir)
        out_file = output_dir / f"lines__{trainer_path.stem}.molang"
        out_file.write_text(molang_text, encoding="utf-8")


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "trainer_lines"
    trainers_folder = base_dir / "trainers"
    data_folder = base_dir / "data"
    output_folder = base_dir /".." / ".." / "molang" / "trainer_lines"
    compile_all_trainers(trainers_folder, data_folder, output_folder)