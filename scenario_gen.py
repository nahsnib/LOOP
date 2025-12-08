# scenario_gen.py
import random
from settings import CHARACTERS_DB, SCRIPTS_DB
from models import Character

class ScenarioBuilder:
    def build(self):
        print("🎲 正在構築本輪迴的劇本...")
        all_chars = [Character(*data) for data in CHARACTERS_DB]
        selected_chars = random.sample(all_chars, 12)
        print(f"   -> 已選定 {len(selected_chars)} 名登場人物")

        # 從 settings.py (載入自 JSON) 的資料庫中選取
        main_script = random.choice(SCRIPTS_DB["Main"])
        sub_script = random.choice(SCRIPTS_DB["Sub"])
        print(f"   -> 主軸：{main_script['name']} | 支線：{sub_script['name']}")

        available_chars = selected_chars.copy()
        random.shuffle(available_chars)
        
        all_roles_req = []
        all_roles_req.extend(main_script['roles'])
        all_roles_req.extend(sub_script['roles'])

        for req in all_roles_req:
            role_name = req['name']
            count = req['count']
            gender_filter = req.get('gender')

            for _ in range(count):
                candidates = [c for c in available_chars if gender_filter is None or c.gender == gender_filter]
                if not candidates:
                    candidates = available_chars
                
                if candidates:
                    chosen = candidates.pop(0)
                    chosen.role = role_name
                    available_chars.remove(chosen)
        
        return selected_chars, [main_script, sub_script]