import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "ccs" / "bedrock" / "npcs" / "src_variations"
OUTPUT_VARIATIONS_DIR = BASE_DIR / "ccs" / "bedrock" / "npcs" / "variations"
TEXTURES_ROOT = BASE_DIR
BAKED_TEXTURE_DIR = BASE_DIR / "ccs" / "textures" / "npcs" / "baked"
SPRITE_OUTPUT_DIR = BASE_DIR / "xaerominimap" / "entity" / "icon" / "sprite" / "ccs"
DEFINITION_OUTPUT_DIR = BASE_DIR / "xaerominimap" / "entity" / "icon" / "definition" / "cobblemon"

def resolve_path(texture_str: str) -> Path:
    ns, path = texture_str.split(":")
    return TEXTURES_ROOT / ns / "textures" / path.replace("textures/", "", 1)

def build_npc_pipeline():
    variants_map = {}
    
    for json_file in SRC_DIR.glob("**/*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        rel_path = json_file.relative_to(SRC_DIR)
        subfolder = rel_path.parent
        npc_id = json_file.stem
        
        new_variations_list = []
        
        for idx, variation in enumerate(data.get("variations", [])):
            base_tex = variation.get("texture")
            if not base_tex:
                continue
                
            # 1. Composite layers into a single image
            base_path = resolve_path(base_tex)
            if not base_path.exists():
                continue
                
            composite = Image.open(base_path).convert("RGBA")
            for layer in variation.get("layers", []):
                layer_path = resolve_path(layer["texture"])
                if layer_path.exists():
                    layer_img = Image.open(layer_path).convert("RGBA")
                    composite = Image.alpha_composite(composite, layer_img)
            
            # 2. Save baked flat texture for Cobblemon
            baked_rel_path = f"ccs:textures/npcs/baked/{subfolder.as_posix()}/{npc_id}_var_{idx}.png" if subfolder != Path('.') else f"ccs:textures/npcs/baked/{npc_id}_var_{idx}.png"
            baked_abs_path = BAKED_TEXTURE_DIR / subfolder / f"{npc_id}_var_{idx}.png"
            baked_abs_path.parent.mkdir(parents=True, exist_ok=True)
            composite.save(baked_abs_path)
            
            # 3. Crop face for Xaero minimap sprite
            face_base = composite.crop((8, 8, 16, 16))
            face_hat = composite.crop((40, 8, 48, 16))
            face_composite = Image.alpha_composite(face_base, face_hat)
            
            icon_canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            icon_canvas.paste(face_composite.resize((16,16), Image.Resampling.NEAREST), (24, 24))
            
            sprite_sub = f"{subfolder.as_posix()}/" if subfolder != Path('.') else ""
            sprite_filename = f"{npc_id}_var_{idx}.png"
            sprite_filepath = SPRITE_OUTPUT_DIR / subfolder / sprite_filename
            sprite_filepath.parent.mkdir(parents=True, exist_ok=True)
            icon_canvas.save(sprite_filepath)
            
            # 4. Map unique baked texture to outlined sprite in Xaero definition
            variants_map[baked_rel_path] = f"outlined_sprite:ccs/{sprite_sub}{sprite_filename}"
            
            # 5. Build clean new variation entry (no layers needed anymore)
            new_variations_list.append({
                "aspects": variation.get("aspects", []),
                "poser": variation.get("poser", "cobblemon:standard"),
                "model": variation.get("model", "cobblemon:steve.geo"),
                "texture": baked_rel_path
            })
            
        # Write clean output variation JSON
        new_npc_data = {
            "name": data.get("name"),
            "order": data.get("order", 0),
            "variations": new_variations_list
        }
        
        out_json_path = OUTPUT_VARIATIONS_DIR / subfolder / f"{npc_id}.json"
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(new_npc_data, f, indent=2)

    # Output Xaero definition JSON
    variants_map["default"] = "model:0"
    DEFINITION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFINITION_OUTPUT_DIR / "npc.json", "w", encoding="utf-8") as f:
        json.dump({"variants": variants_map, "modelConfigs": [{"baseScale": 1.0}]}, f, indent=4)
        
    print("✅ Successfully generated baked textures, clean NPC variations, and Xaero definitions!")

if __name__ == "__main__":
    build_npc_pipeline()