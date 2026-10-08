import json
import os
import copy

CATEGORIES = [
    "center",
    "decos",
    "foundations",
    "houses/1x1",
    "houses/2x1",
    "houses/2x2",
    "houses/3x2",
    "houses/start",
    "roads",
    "city_npc"
]
OUTPUT_DIR = "worldgen/template_pool/"
TOWNS = [
    "viridian",
    "cinnabar",
    "saffron",
    "fuchsia",
    "celadon",
    "vermilion",
    "cerulean",
    "pewter"
    # "lavender",
]

def replace_town_id(obj, town_name):
    """Recursively replaces #town_id with town_name in strings within dicts, lists, or raw strings."""
    if isinstance(obj, str):
        return obj.replace("#town_id", town_name)
    elif isinstance(obj, dict):
        return {k: replace_town_id(v, town_name) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_town_id(elem, town_name) for elem in obj]
    return obj

def normalize_element(item, town_name, processor_id, library=None):
    if library is None:
        library = {}
        
    if isinstance(item, str):
        if item in library:
            item = library[item]
        else:
            print(f"Warning: Placeholder '{item}' not found in library.")
            return []

    if isinstance(item, list):
        normalized_list = []
        for sub_item in item:
            res = normalize_element(sub_item, town_name, processor_id, library)
            if res:
                if isinstance(res, list):
                    normalized_list.extend(res)
                else:
                    normalized_list.append(res)
        return normalized_list

    item_copy = copy.deepcopy(item)
    
    if "element" in item_copy and isinstance(item_copy["element"], dict):
        weight = item_copy.get("weight", 1)
        elem = item_copy["element"]
        element_type = elem.get("element_type", "minecraft:single_pool_element")
        
        if "delegate" in elem and isinstance(elem["delegate"], dict):
            del_elem = elem["delegate"]
            del_elem.setdefault("element_type", "minecraft:single_pool_element")
            del_elem.setdefault("projection", "rigid")
            
            if "processors" not in del_elem or del_elem["processors"] == "placeholder_processor" or not del_elem["processors"]:
                del_elem["processors"] = processor_id
                
        elif "empty_pool_element" in element_type:
            return {
                "weight": weight,
                "element": {
                    "element_type": element_type
                }
            }
        else:
            elem.setdefault("element_type", "minecraft:single_pool_element")
            elem.setdefault("projection", "rigid")
            if "processors" not in elem or elem["processors"] == "placeholder_processor" or not elem["processors"]:
                elem["processors"] = processor_id
                
        return replace_town_id(item_copy, town_name)
    
    weight = item_copy.pop("weight", 1)
    element_type = item_copy.pop("element_type", "minecraft:single_pool_element")
    
    if "empty_pool_element" in element_type:
        return {
            "weight": weight,
            "element": {
                "element_type": element_type
            }
        }
        
    location = item_copy.pop("location", "")
    projection = item_copy.pop("projection", "rigid")
    processors = item_copy.pop("processors", processor_id)
    
    if processors == "placeholder_processor" or not processors:
        processors = processor_id
        
    elem = {
        "element_type": element_type,
        "location": location,
        "processors": processors,
        "projection": projection
    }
    elem.update(item_copy)
    
    result = {
        "weight": weight,
        "element": elem
    }
    return replace_town_id(result, town_name)

def generate_template_pools():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for category in CATEGORIES:
        cat_path_parts = category.split("/")
        shared_template_path = os.path.join("worldgen", "src", *cat_path_parts, "shared.json")
        towns_dir = os.path.join("worldgen", "src", *cat_path_parts, "towns")
        
        if not os.path.exists(shared_template_path):
            print(f"Skipping [{category}]: Shared template not found at {shared_template_path}")
            continue
            
        with open(shared_template_path, "r", encoding="utf-8") as f:
            base_template = json.load(f)

        shared_library = base_template.get("library", {})
        default_shared_elements = base_template.get("elements", [])

        for town_name in TOWNS:
            town_path = os.path.join(towns_dir, f"{town_name}.json")
            
            town_elements_input = []
            if os.path.exists(town_path):
                with open(town_path, "r", encoding="utf-8") as f:
                    town_elements_input = json.load(f)
                
            pool_output = replace_town_id(base_template, town_name)
            
            if "library" in pool_output:
                del pool_output["library"]
            if "elements" in pool_output:
                del pool_output["elements"]
                
            processor_id = f"ccs:{town_name}/general"
            # processor_id = "minecraft:empty"
            
            processed_shared = []
            for item in default_shared_elements:
                normalized = normalize_element(item, town_name, processor_id, shared_library)
                if normalized:
                    if isinstance(normalized, list):
                        processed_shared.extend(normalized)
                    else:
                        processed_shared.append(normalized)
                
            resolved_town_elements = []
            for item in town_elements_input:
                normalized = normalize_element(item, town_name, processor_id, shared_library)
                if normalized:
                    if isinstance(normalized, list):
                        resolved_town_elements.extend(normalized)
                    else:
                        resolved_town_elements.append(normalized)
                    
            pool_output["elements"] = processed_shared + resolved_town_elements
            
            out_file_path = os.path.join(OUTPUT_DIR, town_name, f"{category}.json")
            os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
            
            with open(out_file_path, "w", encoding="utf-8") as f:
                json.dump(pool_output, f, indent=4)
                
            print(f"Successfully generated template pool for {town_name} [{category}] -> {out_file_path}")

if __name__ == "__main__":
    generate_template_pools()