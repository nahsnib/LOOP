# mechanics.py
from settings import STATION_ID, MAP_SIZE

def check_sanity_status(char, log_func=print):
    if char.sanity <= 0 and not char.is_dead:
        log_func(f"      😱 {char.name} 精神崩潰！(Sanity <= 0)")

def send_to_station(char, log_func=print):
    log_func(f"      🛑 {char.name} 被強制轉移至車站，精神 -1")
    char.location = STATION_ID
    char.sanity -= 1
    check_sanity_status(char, log_func)

def process_arrival(char, new_location, log_func=print):
    char.location = new_location
    if new_location == STATION_ID:
        return
    region = new_location // 3
    if region == char.forbidden_region:
        log_func(f"   ⚠️  [警告] {char.name} 誤入禁地 (區域{region})！")
        send_to_station(char, log_func)

def calculate_sunrise_move(current_loc):
    if current_loc == STATION_ID:
        return STATION_ID
    return (current_loc - 1) % MAP_SIZE