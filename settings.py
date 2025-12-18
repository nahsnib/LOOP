# settings.py
import json
import os

# === 地點與全域設定 ===
STATION_ID = 4  # 特殊地點 ID (車站、駕駛台、中央控制室等)
NUM_LOCATIONS = 5  # 地點總數 (0, 1, 2, 3, 4)

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
DEFAULT_SCRIPTS_DB = {
    "Role_Data": {},
    "Main": [],
    "Sub": [],
    "Foreshadow": []
}

def load_scripts():
    """從 JSON 檔案讀取劇本，並提供更健壯的錯誤處理"""
    file_path = os.path.join(os.getcwd(), "scripts.json")  # 確保路徑讀取正確
    try:
        if not os.path.exists(file_path):
            print(f"⚠️ 注意：找不到 {file_path}，已使用默認空結構。")
            return DEFAULT_SCRIPTS_DB

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)  # 讀取 JSON

    except json.JSONDecodeError as e:
        print(f"❌ JSON 檔案無法解析: {e}")
        return DEFAULT_SCRIPTS_DB

    except Exception as e:
        print(f"❌ 錯誤發生，無法讀取 {file_path}: {e}")
        return DEFAULT_SCRIPTS_DB

# 初始化全域變數
SCRIPTS_DB = load_scripts()

if __name__ == "__main__":
    # 測試代碼
    print("SCRIPTS_DB:", SCRIPTS_DB)
