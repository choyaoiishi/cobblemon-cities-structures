import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).parent
SRC_DIR = BASE_DIR / "ccs" / "bedrock" / "npcs" / "variations"
TEXTURES_ROOT = BASE_DIR
SPRITE_OUTPUT_DIR = BASE_DIR / "xaerominimap" / "entity" / "icon" / "sprite" / "ccs"
DEFINITION_OUTPUT_DIR = BASE_DIR / "xaerominimap" / "entity" / "icon" / "definition" / "cobblemon"

def resolve_path(texture_str: str) -> Path:
    ns, path = texture_str.split(":")
    return TEXTURES_ROOT / ns / "textures" / path.replace("textures/", "", 1)

def build_xaero_icons():
    variants_map = {}
    
    for json_file in SRC_DIR.glob("**/*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        rel_path = json_file.relative_to(SRC_DIR)
        subfolder = rel_path.parent
        npc_id = json_file.stem
        
        for idx, variation in enumerate(data.get("variations", [])):
            base_tex = variation.get("texture")
            if not base_tex:
                continue
                
            # 1. Composite layers into a single image for face cropping
            base_path = resolve_path(base_tex)
            if not base_path.exists():
                continue
                
            composite = Image.open(base_path).convert("RGBA")
            for layer in variation.get("layers", []):
                layer_path = resolve_path(layer["texture"])
                if layer_path.exists():
                    layer_img = Image.open(layer_path).convert("RGBA")
                    # Ensure layer matches base dimensions (fixes placeholder size mismatch)
                    if layer_img.size != composite.size:
                        layer_img = layer_img.resize(composite.size, Image.Resampling.NEAREST)
                    composite = Image.alpha_composite(composite, layer_img)
            
            # 2. Crop face for Xaero minimap sprite
            face_base = composite.crop((8, 8, 16, 16))
            face_hat = composite.crop((40, 8, 48, 16))
            face_composite = Image.alpha_composite(face_base, face_hat)
            
            icon_canvas = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            icon_canvas.paste(face_composite.resize((16, 16), Image.Resampling.NEAREST), (24, 24))
            
            sprite_sub = f"{subfolder.as_posix()}/" if subfolder != Path('.') else ""
            sprite_filename = f"{npc_id}_var_{idx}.png"
            sprite_filepath = SPRITE_OUTPUT_DIR / subfolder / sprite_filename
            sprite_filepath.parent.mkdir(parents=True, exist_ok=True)
            icon_canvas.save(sprite_filepath)
            
            # 3. Map original texture to outlined sprite in Xaero definition
            variants_map[base_tex] = f"outlined_sprite:ccs/{sprite_sub}{sprite_filename}"
            
    # Output Xaero definition JSON
    variants_map["default"] = "model:0"
    DEFINITION_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(DEFINITION_OUTPUT_DIR / "npc.json", "w", encoding="utf-8") as f:
        json.dump({"variants": variants_map, "modelConfigs": [{"baseScale": 1.0}]}, f, indent=4)
        
    print("✅ Successfully generated Xaero minimap icons and definition!")

if __name__ == "__main__":
    build_xaero_icons()