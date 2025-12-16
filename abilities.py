# abilities.py
import random
from settings import STATION_ID
from mechanics import check_sanity_status

def ability_kill_target(actor, all_chars, log_func=print):
    """夜晚殺人 (殺手/恐怖份子/吸血鬼/私生子 通用)"""
    loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead and c != actor]
    if loc_chars:
        target = random.choice(loc_chars)
        target.is_dead = True
        log_func(f"   🔪 {actor.name} 在黑暗中殺害了 {target.name}。")

def ability_mastermind(actor, all_chars, log_func=print):
    """黃昏：黑幕/邪教徒 - 增加陰謀"""
    loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead and c != actor]
    if loc_chars:
        target = random.choice(loc_chars)
        if target.intrigue == 0:
            target.intrigue = 1
            log_func(f"   😈 {actor.name} 使 {target.name} 陷入陰謀。")

def ability_spread_chaos(actor, all_chars, log_func=print):
    """黃昏：煽動者/散播者 - 降低精神 (單一目標)"""
    loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead and c != actor]
    if loc_chars:
        target = random.choice(loc_chars)
        target.sanity -= 1
        log_func(f"   🗣️ {actor.name} 散播謠言，{target.name} 精神 -1。")
        check_sanity_status(target, log_func)

def ability_cultist_sunrise(actor, all_chars, log_func=print):
    """日出：邪教徒 - 移動到關鍵人物位置"""
    key_person = next((c for c in all_chars if c.role == "關鍵人物" and not c.is_dead), None)
    if key_person and actor.location != key_person.location:
        actor.location = key_person.location
        log_func(f"   🏃 {actor.name} 追隨領袖，移動至 Loc {key_person.location}。")

def ability_cultist_night(actor, all_chars, log_func=print):
    """夜晚：邪教徒 - 在車站與戀人匯合 (僅紀錄事件，無實質作用)"""
    mad_lover = next((c for c in all_chars if c.role == "瘋狂的戀人" and not c.is_dead), None)
    if actor.location == STATION_ID and mad_lover and mad_lover.location == STATION_ID:
        log_func(f"   💞 {actor.name} 與戀人在車站秘密會面。")

def ability_avenger(actor, all_chars, log_func=print):
    """黃昏：復仇者 - 追殺目標 (移動到目標位置)"""
    target = next((c for c in all_chars if c.role == "關鍵人物" and not c.is_dead), None)
    if target and actor.location != target.location:
        actor.location = target.location
        log_func(f"   🎯 {actor.name} 被仇恨驅使，追擊 {target.name}。")

def ability_mad_lover(actor, all_chars, log_func=print):
    """夜晚：瘋狂的戀人 - 殺害非戀人的同伴"""
    partner = next((c for c in all_chars if c.role == "溫和的戀人" and not c.is_dead and c != actor), None)
    if partner and actor.location == partner.location:
        # 殺死所有同地點的非戀人
        loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead and c.role not in ["溫和的戀人", "瘋狂的戀人"]]
        if loc_chars:
            target = random.choice(loc_chars)
            target.is_dead = True
            log_func(f"   💔 {actor.name} 因愛發狂，殺害了 {target.name}。")

# 新增：帶原者 (擴散給所有同區目標)
def ability_carrier(actor, all_chars, log_func=print):
    """黃昏：帶原者 - 擴散病原體 (全員精神-1)"""
    loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead and c != actor]
    if loc_chars:
        log_func(f"   ☣️ {actor.name} 散播了病原體...")
        for target in loc_chars:
            target.sanity -= 1
            log_func(f"      -> {target.name} 感到身體不適 (精神-1)")
            check_sanity_status(target, log_func)

# 新增：吸血鬼 (若與他人獨處則殺人)
def ability_vampire_logic(actor, all_chars, log_func=print):
    """夜晚：吸血鬼 - 獨處時殺人 (人數為 2)"""
    loc_chars = [c for c in all_chars if c.location == actor.location and not c.is_dead]
    # 如果只有自己和另一個人 (共2人)
    if len(loc_chars) == 2:
        target = [c for c in loc_chars if c != actor][0]
        target.is_dead = True
        log_func(f"   🧛 {actor.name} 吸乾了 {target.name} 的血。")


# 角色能力映射表
ROLE_ABILITIES = {
    # 殺人類
    "殺手":   {"night": ability_kill_target},
    "恐怖份子": {"night": ability_kill_target}, 
    "連環殺手": {"night": ability_kill_target}, 
    "私生子":   {"night": ability_kill_target}, 
    "吸血鬼": {"night": ability_vampire_logic}, # 劇本4

    # 陰謀/精神類 (黃昏)
    "黑幕":   {"dusk": ability_mastermind},
    "散播者": {"dusk": ability_spread_chaos},
    "煽動者": {"dusk": ability_spread_chaos},
    "帶原者": {"dusk": ability_carrier}, # 劇本3
    
    # 特殊行動類
    "邪教徒": {"sunrise": ability_cultist_sunrise, "night": ability_cultist_night},
    "復仇者": {"dusk": ability_avenger},
    "瘋狂的戀人": {"night": ability_mad_lover},
}
