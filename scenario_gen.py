# scenario_gen.py
import random
import json
import os
from models import Character
from settings import TOTAL_CHARS, NAMES, STATION_ID

class ScenarioBuilder:
    def __init__(self, script_file='scripts.json'):
        # 確保檔案存在，如果不存在則跳過讀取或報錯
        if not os.path.exists(script_file):
            raise FileNotFoundError(f"找不到劇本檔案: {script_file}，請確保 scripts.json 存在於同目錄。")
            
        with open(script_file, 'r', encoding='utf-8') as f:
            self.scripts = json.load(f)
            
    def _select_script_parts(self):
        """從三個部分各隨機選擇一個，確保三個ID開頭來自不同的劇本主題 (1XX, 2XX, 3XX, 4XX)"""
        
        # 確保主軸、支線、伏筆來自三個不同的劇本 ID 類別
        all_ids = list(range(1, 5)) # [1, 2, 3, 4]
        random.shuffle(all_ids)
        
        # 選擇主軸 (Main)
        main_part = random.choice([s for s in self.scripts['Main'] if s['id'].startswith(str(all_ids[0]))])
        
        # 選擇支線 (Sub)，確保 ID 來自不同的類別
        sub_id_pool = [i for i in all_ids if i != all_ids[0]]
        sub_part = random.choice([s for s in self.scripts['Sub'] if s['id'].startswith(str(random.choice(sub_id_pool)))])
        
        # 選擇伏筆 (Foreshadow)，確保 ID 來自尚未使用的類別
        foreshadow_id_pool = [i for i in all_ids if i != all_ids[0] and i != int(sub_part['id'][0])]
        foreshadow_part = random.choice([s for s in self.scripts['Foreshadow'] if s['id'].startswith(str(random.choice(foreshadow_id_pool)))])
        
        return [main_part, sub_part, foreshadow_part]

    def _generate_characters(self, selected_parts):
        """根據選擇的劇本部分生成人物列表"""
        
        # 1. 收集所有指定角色
        required_roles = []
        for part in selected_parts:
            for role_info in part.get('roles', []):
                for _ in range(role_info['count']):
                    required_roles.append(role_info)

        # 2. 隨機選擇剩餘的人名
        available_names = list(NAMES) # 格式: (姓名, 性別)
        random.shuffle(available_names)
        
        # 3. 確定人物列表
        characters = []
        
        # 3a. 分配指定角色
        for role_info in required_roles:
            
            name, gender_check = available_names.pop(0)
            
            # 嘗試匹配性別 (如果劇本要求特定性別)
            required_gender = role_info.get('gender')
            if required_gender in ['F', 'M']:
                 # 如果當前名字不匹配，從剩餘名單中找一個匹配的
                if gender_check != required_gender:
                    found_index = -1
                    for i, (n, g) in enumerate(available_names):
                        if g == required_gender:
                            # 找到匹配，交換並使用
                            name_match, gender_match = available_names.pop(i)
                            available_names.insert(0, (name, gender_check)) # 將不匹配的原名放回名單最前
                            name, gender_check = name_match, gender_match # 使用匹配的名單
                            break
            
            # 初始位置隨機分配 (0-4)
            location = random.randint(0, 4)
            
            # 創建 Character 物件 (初始 sanity=3, intrigue=0)
            char = Character(name, gender_check, location, role=role_info['name'])
            characters.append(char)

        # 3b. 填補一般人
        num_general = TOTAL_CHARS - len(characters)
        for _ in range(num_general):
            if available_names:
                name, gender = available_names.pop(0)
                location = random.randint(0, 4)
                char = Character(name, gender, location, role="一般人")
                characters.append(char)
        
        random.shuffle(characters)
        return characters

    def build(self):
        """創建遊戲情境，返回人物列表和劇本列表"""
        selected_parts = self._select_script_parts()
        characters = self._generate_characters(selected_parts)
        return characters, selected_parts
