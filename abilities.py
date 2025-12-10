# abilities.py
from mechanics import check_sanity_status

def get_targets_in_same_region(actor, all_chars):
    if actor.location == -1: return []
    region = actor.location // 3
    return [c for c in all_chars if c.location != -1 and (c.location // 3) == region and c != actor]

def ability_killer(actor, all_chars, log_func=print):
    targets = get_targets_in_same_region(actor, all_chars)
    if targets:
        victim = min(targets, key=lambda x: x.sanity)
        log_func(f"   🔪 [殺手] {actor.name} 在陰影中現身，殺害了 {victim.name}！")
        victim.is_dead = True
        victim.sanity = 0

def ability_spreader(actor, all_chars, log_func=print):
    targets = get_targets_in_same_region(actor, all_chars)
    if targets:
        log_func(f"   👿 [散播者] {actor.name} 散布了謠言...")
        for t in targets:
            log_func(f"      -> {t.name} 感到恐慌 (精神-1)")
            t.sanity -= 1
            check_sanity_status(t, log_func)

def ability_cultist(actor, all_chars, log_func=print):
    targets = get_targets_in_same_region(actor, all_chars)
    if targets:
        log_func(f"   🙏 [邪教徒] {actor.name} 正在進行詭異的儀式...")
        for t in targets:
            t.sanity -= 1
            check_sanity_status(t, log_func)

ROLE_ABILITIES = {
    "殺手": {"night": ability_killer},
    "散播者": {"dusk": ability_spreader},
    "邪教徒": {"dusk": ability_cultist},
}