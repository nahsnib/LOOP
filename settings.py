# settings.py
import json
import os

# === 地圖與全域設定 ===
MAP_SIZE = 12
STATION_ID = -1

# === 角色資料庫 ===
# 格式: (ID, 姓名, 預設位置, 性別, 初始精神, 禁地代號)
# 禁地代號: 0:神社(0-2), 1:醫院(3-5), 2:都市(6-8), 3:學校(9-11), -1:無
CHARACTERS_DB = [
    (1, "巫女", 0, "F", 2, 2),
    (2, "耆老", 1, "M", 3, 3),
    (3, "異鄉人", 2, "F", 2, 1),
    (4, "醫生", 3, "F", 3, 0),
    (5, "病患", 4, "F", 1, 2),
    (6, "記者", 5, "M", 2, 3),
    (7, "酒保", 6, "M", 2, 0),
    (8, "警察", 7, "M", 3, 1),
    (9, "上班族", 8, "M", 2, 3),
    (10, "男學生", 9, "M", 2, 1),
    (11, "女學生", 10, "F", 2, 2),
    (12, "教師", 11, "M", 2, 0),
    (13, "流浪漢", -1, "M", 1, -1),
    (14, "遊客", -1, "F", 2, -1),
    (15, "占卜師", -1, "F", 2, -1)
]

# === 劇本資料庫 (JSON讀取) ===
def load_scripts():
    """從 JSON 檔案讀取劇本"""
    file_path = "scripts.json"
    if not os.path.exists(file_path):
        return {"Main": [], "Sub": []}
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

SCRIPTS_DB = load_scripts()