import json
import os
import shutil


def load_aspect_mapping(filepath="aspect_mapping.json"):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_boss_data(filepath="bosses.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_and_save_teams(trainer_mapping, output_folder="team_data"):
    # Clear output folder completely before writing new files
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    data = load_boss_data("bosses.json")
    aspect_mapping = load_aspect_mapping("aspect_mapping.json")

    for title, base_name in trainer_mapping.items():
        defaults = []
        for cat in data.get("default", {}).get("categories", []):
            for boss in cat.get("bosses", []):
                if boss.get("title") == title:
                    defaults.append(boss)

        hardcores = []
        for cat in data.get("hardcore", {}).get("categories", []):
            for boss in cat.get("bosses", []):
                if boss.get("title") == title:
                    hardcores.append(boss)

        interleaved_teams = []
        max_len = max(len(defaults), len(hardcores))
        for i in range(max_len):
            if i < len(defaults):
                interleaved_teams.append(("default", i + 1, defaults[i]))
            if i < len(hardcores):
                interleaved_teams.append(("hardcore", i + 1, hardcores[i]))

        print(f"Processing '{title}': Found {len(interleaved_teams)} team entries.")

        for global_idx, (mode, team_num, boss_data) in enumerate(
            interleaved_teams, 1
        ):
            filename = f"{base_name}_{global_idx}.json"
            filepath = os.path.join(output_folder, filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            processed_pokemon = []
            for p in boss_data.get("pokemon", []):
                p_copy = p.copy()
                species = p_copy.get("species", "")

                if "Mega" in species or "-Mega" in species:
                    p_copy["item"] = ""

                if species in aspect_mapping:
                    p_copy["aspect"] = aspect_mapping[species]
                    p_copy["species"] = species.split("-")[0]
                else:
                    pass

                processed_pokemon.append(p_copy)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(processed_pokemon, f, indent=2)

            print(
                f"  -> Saved {filepath} ({mode} team {team_num} |"
                f" {len(processed_pokemon)} Pokémon)"
            )


if __name__ == "__main__":
    trainers_to_extract = {
        "GYM LEADER · BROCK": "leaders/brock",
        "GYM LEADER · MISTY": "leaders/misty",
        "GYM LEADER · LT. SURGE": "leaders/lt_surge",
        "GYM LEADER · ERIKA": "leaders/erika",
        "GYM LEADER · SABRINA": "leaders/sabrina",
        "GYM LEADER · KOGA": "leaders/koga",
        "GYM LEADER · BLAINE": "leaders/blaine",
        "GYM LEADER · CLAIR": "leaders/clair",
        "GIOVANNI": "rockets/giovanni",
        "ARCHER": "rockets/archer",
        "ariana": "rockets/ariana",
        "ariana_archer": "rockets/ariana_archer",
        "rival": "rival/terry",
        "brendan": "rival/brendan",
        "may": "rival/may",
    }

    extract_and_save_teams(trainers_to_extract, output_folder="team_data")