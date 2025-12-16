# settings.py
import json
import os

# === 地點與全域設定 ===
STATION_ID = 4 # 特殊地點 ID (車站、駕駛台、中央控制室等)
NUM_LOCATIONS = 5 # 地點總數 (0, 1, 2, 3, 4)

# === 遊戲通用常數 ===
TOTAL_CHARS = 8 
MAX_DAYS = 4

# === 角色資料庫 (用於隨機分配名字和職業背景) ===
# 格式: (姓名, 性別)
NAMES = [
    ("巫女", "F"), ("耆老", "M"), ("異鄉人", "F"), ("醫生", "F"), 
    ("記者", "M"), ("警察", "M"), ("教師", "M"), ("占卜師", "F")
]

# === 劇本資料庫 (JSON讀取) ===
# 保持原有的 JSON 讀取邏輯
def load_scripts():
    """從 JSON 檔案讀取劇本"""
    file_path = "scripts.json"
    if not os.path.exists(file_path):
        # 應返回一個空結構以避免程式崩潰
        return {"Main": [], "Sub": [], "Foreshadow": []} 
        
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

SCRIPTS_DB = load_scripts()
