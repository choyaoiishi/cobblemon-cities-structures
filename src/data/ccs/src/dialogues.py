import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
SRC_DIALOGUES_DIR = BASE_DIR / "dialogues"
TEMPLATE_PATH = SRC_DIALOGUES_DIR / "templates" / "dialogue.json"
REWARD_TEMPLATE_PATH = SRC_DIALOGUES_DIR / "templates" / "reward.json"
BATTLE_TEMPLATE_PATH = SRC_DIALOGUES_DIR / "templates" / "battle.json"
TRADE_TEMPLATE_PATH = SRC_DIALOGUES_DIR / "templates" / "trade.json"
SHOP_TEMPLATE_PATH = SRC_DIALOGUES_DIR / "templates" / "shop.json"
OUTPUT_DIALOGUES_DIR = BASE_DIR / ".." / "dialogues" / "generated"

def build_dialogue_files():
    base_template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8")) if TEMPLATE_PATH.exists() else {}
    
    reward_raw = REWARD_TEMPLATE_PATH.read_text(encoding="utf-8") if REWARD_TEMPLATE_PATH.exists() else "[]"
    battle_raw = BATTLE_TEMPLATE_PATH.read_text(encoding="utf-8") if BATTLE_TEMPLATE_PATH.exists() else "[]"
    trade_raw = TRADE_TEMPLATE_PATH.read_text(encoding="utf-8") if TRADE_TEMPLATE_PATH.exists() else "[]"
    shop_raw = SHOP_TEMPLATE_PATH.read_text(encoding="utf-8") if SHOP_TEMPLATE_PATH.exists() else "[]"

    for json_file in SRC_DIALOGUES_DIR.glob("*.json"):
        prefix_name = json_file.stem
        entries = json.loads(json_file.read_text(encoding="utf-8"))
        entries_iter = entries.items() if isinstance(entries, dict) else enumerate(entries)

        for entry_key, entry in entries_iter:
            custom_id = str(entry_key)
            lines = entry.get("lines", [])
            battle_data = entry.get("battle")
            reward_data = entry.get("reward")
            trade_data = entry.get("trade")
            shop_data = entry.get("shop")
            
            has_battle = bool(battle_data)
            has_reward = bool(reward_data)
            has_trade = bool(trade_data)
            has_shop = bool(shop_data)

            # Parse shorthand arrays safely
            b_trainer = b_battle = b_win = b_won = b_adv = b_min_level = ""
            b_type = "single"
            if has_battle and isinstance(battle_data, list):
                b_trainer = battle_data[0] if len(battle_data) > 0 else ""
                b_battle = battle_data[1] if len(battle_data) > 1 else ""
                b_win = battle_data[2] if len(battle_data) > 2 else ""
                b_won = battle_data[3] if len(battle_data) > 3 else ""
                b_min_level = battle_data[4] if len(battle_data) > 4 else ""
                b_adv = battle_data[5] if len(battle_data) > 5 else ""
                b_type = battle_data[6] if len(battle_data) > 6 and battle_data[6] else "single"

            r_type = r_val = r_give = r_take = ""
            if has_reward and isinstance(reward_data, list) and len(reward_data) >= 4:
                r_type, r_val, r_give, r_take = reward_data[0], reward_data[1], reward_data[2], reward_data[3]

            t_target_id = t_target_name = t_pokemon_id = t_pokemon_name = t_nick = ""
            if has_trade and isinstance(trade_data, list):
                t_target_id = trade_data[0] if len(trade_data) > 0 else ""
                t_target_name = trade_data[1] if len(trade_data) > 1 else ""
                t_pokemon_id = trade_data[2] if len(trade_data) > 2 else ""
                t_pokemon_name = trade_data[3] if len(trade_data) > 3 else ""
                t_nick = trade_data[4] if len(trade_data) > 4 else ""

            s_shop_id = s_bank_id = s_shop_text = s_bye_text = ""
            if has_shop and isinstance(shop_data, list):
                s_shop_id = shop_data[0] if len(shop_data) > 0 else ""
                s_bank_id = shop_data[1] if len(shop_data) > 1 else ""
                s_shop_text = shop_data[2] if len(shop_data) > 2 else ""
                s_bye_text = shop_data[3] if len(shop_data) > 3 else ""

            # Unified replacement map
            replacements = {
                "#battle_text": b_battle,
                "#win_text": b_win,
                "#won_text": b_won,
                "#give_text": r_give,
                "#take_text": r_take,
                "#trainer_id": b_trainer,
                "#advancement": b_adv,
                "#battle_type": b_type,
                "#min_level": b_min_level,
                "#reward_type": r_type,
                "#reward_value": r_val,
                "#target_id": t_target_id,
                "#target_name": t_target_name,
                "#pokemon_id": t_pokemon_id,
                "#pokemon_name": t_pokemon_name,
                "#nickname": t_nick,
                "#shop_id": s_shop_id,
                "#bank_id": s_bank_id,
                "#shop_text": s_shop_text,
                "#bye_text": s_bye_text,
            }

            pages = []

            if has_trade:
                template_str = trade_raw
                for placeholder, val in replacements.items():
                    escaped_val = json.dumps(str(val))[1:-1]
                    template_str = template_str.replace(placeholder, escaped_val)
                
                trade_pages = json.loads(template_str)
                pages.extend(trade_pages)

            elif has_battle:
                template_str = battle_raw
                for placeholder, val in replacements.items():
                    escaped_val = json.dumps(str(val))[1:-1]
                    template_str = template_str.replace(placeholder, escaped_val)
                
                battle_pages = json.loads(template_str)
                for page in battle_pages:
                    pid = page.get("id")
                    if not has_reward and pid in ["reward_give", "reward_gave"]:
                        continue
                    if not has_reward and pid == "win":
                        page["input"] = [
                            "t.next_page = q.run_script('ccs:battle__landing_win');",
                            "q.dialogue.set_page(t.next_page);"
                        ]
                    pages.append(page)

                if lines:
                    normal_pages = []
                    total = len(lines)
                    for i, text in enumerate(lines):
                        p_num = i + 1
                        action = ["q.dialogue.set_page('battle');"] if p_num == total else [f"q.dialogue.set_page('line_{p_num + 1}');"]
                        normal_pages.append({
                            "id": f"line_{p_num}",
                            "speaker": "npc",
                            "lines": [text],
                            "input": action
                        })
                    pages[1:1] = normal_pages
                else:
                    auto_page = {
                        "id": "line_1",
                        "speaker": "npc",
                        "lines": [],
                        "input": {
                            "type": "auto-continue",
                            "delay": 0.01,
                            "allowSkip": False,
                            "action": "q.dialogue.set_page('battle')"
                        }
                    }
                    pages[1:1] = [auto_page]

            elif has_reward:
                template_str = reward_raw
                for placeholder, val in replacements.items():
                    escaped_val = json.dumps(str(val))[1:-1]
                    template_str = template_str.replace(placeholder, escaped_val)
                
                reward_pages = json.loads(template_str)
                pages.extend(reward_pages)

                total = len(lines)
                for i, text in enumerate(lines):
                    p_num = i + 1
                    action = ["q.dialogue.set_page('reward_give');"] if p_num == total else [f"q.dialogue.set_page('line_{p_num + 1}');"]
                    pages.append({
                        "id": f"line_{p_num}",
                        "speaker": "npc",
                        "lines": [text],
                        "input": action
                    })

            elif has_shop:
                template_str = shop_raw
                for placeholder, val in replacements.items():
                    escaped_val = json.dumps(str(val))[1:-1]
                    template_str = template_str.replace(placeholder, escaped_val)
                
                shop_pages = json.loads(template_str)
                
                if lines:
                    normal_pages = []
                    total = len(lines)
                    for i, text in enumerate(lines):
                        p_num = i + 1
                        action = ["q.dialogue.set_page('shop');"] if p_num == total else [f"q.dialogue.set_page('line_{p_num + 1}');"]
                        normal_pages.append({
                            "id": f"line_{p_num}",
                            "speaker": "npc",
                            "lines": [text],
                            "input": action
                        })
                    pages.extend(normal_pages)
                    pages.extend(shop_pages)
                else:
                    pages.extend(shop_pages)

            else:
                total = len(lines)
                for i, text in enumerate(lines):
                    p_num = i + 1
                    action = ["q.dialogue.close();"] if p_num == total else [f"q.dialogue.set_page('line_{p_num + 1}');"]
                    pages.append({
                        "id": f"line_{p_num}",
                        "speaker": "npc",
                        "lines": [text],
                        "input": action
                    })

            dialogue_json = {
                "speakers": base_template.get("speakers", {
                    "npc": {
                        "name": {"type": "expression", "expression": "q.npc.name"},
                        "face": "q.npc.face();"
                    }
                }),
                "pages": pages
            }

            out_path = OUTPUT_DIALOGUES_DIR / prefix_name / f"{prefix_name}_{custom_id}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(dialogue_json, indent=2), encoding="utf-8")

    print("dialogue generated")

if __name__ == "__main__":
    build_dialogue_files()