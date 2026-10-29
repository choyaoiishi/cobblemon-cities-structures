import json
import os

# Common regional suffixes to exclude
REGIONAL_SUFFIXES = {
    "alola",
    "galar",
    "hisui",
    "paldea",
    "sevii",
    "kanto",
    "johto",
    "hoenn",
    "sinnoh",
    "unova",
    "kalos",
}


def generate_aspect_mapping(
    bosses_filepath="bosses.json", output_filepath="aspect_mapping.json"
):
  if not os.path.exists(bosses_filepath):
    print(f"Error: {bosses_filepath} not found.")
    return

  with open(bosses_filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

  aspect_mapping = {}

  # Traverse bosses data across available sections
  for mode in ["default", "hardcore"]:
    mode_data = data.get(mode, {})
    for cat in mode_data.get("categories", []):
      for boss in cat.get("bosses", []):
        for pokemon in boss.get("pokemon", []):
          species = pokemon.get("species", "")

          if "-" in species:
            # Exclude Mega evolutions
            if "mega" in species.lower():
              continue

            # Exclude regional forms
            parts = species.split("-")
            suffix = parts[-1].lower()
            if suffix in REGIONAL_SUFFIXES:
              continue

            # Map the species to its lowercase suffix aspect
            aspect_mapping[species] = suffix

  # Sort the dictionary alphabetically by keys
  sorted_aspect_mapping = dict(sorted(aspect_mapping.items()))

  # Save the sorted dictionary as a JSON file
  with open(output_filepath, "w", encoding="utf-8") as f:
    json.dump(sorted_aspect_mapping, f, indent=2)

  print(
      f"Successfully generated sorted '{output_filepath}' with"
      f" {len(sorted_aspect_mapping)} entries:"
  )
  for k, v in sorted_aspect_mapping.items():
    print(f"  {k}: {v}")


if __name__ == "__main__":
  generate_aspect_mapping()