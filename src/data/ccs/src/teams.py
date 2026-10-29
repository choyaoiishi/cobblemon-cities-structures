import json
import os
import shutil

def sanitize_name(val):
    if not val:
        return ""
    return str(val).lower().replace(" ", "").replace("-", "")

def convert_team_to_molang(team_list):
    molang_entries = []

    for mon in team_list:
        raw_species = mon.get("species", "")
        
        aspect_str = ""
        if "aspect" in mon:
            raw_aspect = mon.get("aspect")
            if raw_aspect:
                cleaned_aspect = str(raw_aspect).lower().replace(" ", "")
                aspect_str = f"aspect={cleaned_aspect}"
        elif "-" in raw_species:
            parts = raw_species.split("-")
            raw_species = parts[0]
            variant = sanitize_name(parts[1])
            if variant == "alola":
                aspect_str = "aspect=alolan"
            elif variant == "galar":
                aspect_str = "aspect=galarian"
            elif variant == "mega":
                aspect_str = "aspect=mega"
            elif variant == "megay":
                aspect_str = "aspect=mega_y"
            elif variant == "megax":
                aspect_str = "aspect=mega_x"
            elif variant == "hisui":
                aspect_str = "aspect=hisuian"
            elif variant == "paldea":
                aspect_str = "aspect=paldean"
            else:
                aspect_str = f"aspect={variant}"

        species = sanitize_name(raw_species)

        moves_raw = mon.get("moves", [])
        moves = ",".join([sanitize_name(m) for m in moves_raw])
        
        nature = sanitize_name(mon.get("nature", ""))
        ability = sanitize_name(mon.get("ability", ""))

        item_raw = mon.get("item", "")
        if item_raw:
            item_cleaned = str(item_raw).lower().replace(" ", "_").replace("-", "")
            item_str = f"cobblemon:{item_cleaned}"
        else:
            item_str = ""

        components = [
            f"'{species}",
            f"moves={moves}" if moves else "",
            f"nature={nature}" if nature else "",
            f"held_item={item_str}" if item_str else "",
            f"ability={ability}" if ability else "",
            aspect_str
        ]
        
        entry = " ".join([c for c in components if c]) + "'"
        molang_entries.append(f"    {entry}")

    formatted_array = "return q.array(\n" + ",\n".join(molang_entries) + "\n);"
    return formatted_array

def process_folder(input_dir, output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".json"):
                input_path = os.path.join(root, filename)
                
                rel_path = os.path.relpath(root, input_dir)
                target_dir = output_dir if rel_path == "." else os.path.join(output_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
                
                base_name = os.path.splitext(filename)[0]
                output_filename = f"{base_name}.molang"
                output_path = os.path.join(target_dir, output_filename)
                
                try:
                    with open(input_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    molang_output = convert_team_to_molang(data)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(molang_output)
                        
                    print(f"processed: {os.path.join(rel_path, filename)} -> {os.path.join(rel_path, output_filename)}")
                except Exception as e:
                    print(f"error processing {filename}: {e}")

if __name__ == "__main__":
    input_folder = "./team_data"
    output_folder = "./team_molang"
    process_folder(input_folder, output_folder)