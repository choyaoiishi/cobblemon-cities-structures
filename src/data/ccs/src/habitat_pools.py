import json
from pathlib import Path

# set base paths
base_dir = Path(__file__).parent / "../"
input_dir = base_dir / "src" / "habitat_pools"
output_dir = base_dir / "habitat_pools"


def generate_habitat_pools():
  # check if input directory exists
  if not input_dir.exists():
    return

  # create output directory if missing
  output_dir.mkdir(parents=True, exist_ok=True)

  # loop through all json files in input directory
  for input_path in input_dir.glob("*.json"):
    src_data = json.loads(input_path.read_text(encoding="utf-8"))
    default_level = src_data.get("level", "45-47")
    raw_spawns = src_data.get("spawns", [])

    spawn_list = []
    for entry in raw_spawns:
      species = entry[0]
      weight = entry[1] if len(entry) > 1 else 20.0
      bucket = entry[2] if len(entry) > 2 else "common"
      phases = entry[3] if len(entry) > 3 else "1-5"

      spawn_entry = {
          "species": species,
          "bucket": bucket,
          "spawnablePositionType": "grounded",
          "weight": float(weight),
          "levelRange": default_level,
          "phases": phases,
      }
      spawn_list.append(spawn_entry)

    output_data = {
        "name": input_path.stem,
        "type": "cobblemon:natural",
        "spawns": spawn_list,
    }

    output_path = output_dir / input_path.name
    output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")


if __name__ == "__main__":
  generate_habitat_pools()