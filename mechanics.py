# mechanics.py
import random
from settings import STATION_ID

def check_sanity_status(char, log_func):
    """檢查並處理人物精神狀態"""
    if char.sanity <= 0 and not char.is_dead:
        char.sanity = 0
        char.intrigue = 1 # 精神崩潰會被黑幕盯上，獲得陰謀狀態
        log_func(f"   ⚠️ {char.name} 精神崩潰，獲得陰謀狀態！")

def calculate_sunrise_move(current_loc):
    """計算日出時的自動移動 (僅限 Loc 0, 1, 2, 3)"""
    if current_loc == STATION_ID:
        return current_loc
    
    # 50% 機率不動
    if random.random() < 0.5:
        return current_loc
    
    # 50% 機率移動到相鄰地點 (環形移動)
    direction = random.choice([-1, 1])
    new_loc = (current_loc + direction) % 4
    return new_loc

def process_arrival(char, new_loc, log_func):
    """處理人物抵達新地點後的邏輯"""
    char.location = new_loc
    
    # 車站邏輯：如果從非車站移動到車站，且精神值高，有機會解除陰謀
    if new_loc == STATION_ID and char.intrigue > 0 and char.sanity > 2 and random.random() < 0.1:
        char.intrigue = 0
        log_func(f"   ✨ {char.name} 在車站得到平靜，解除陰謀。")
