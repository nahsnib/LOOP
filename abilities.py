# abilities.py
import random
from mechanics import check_sanity_status

class AbilityEngine:
    def __init__(self, role_metadata):
        """
        :param role_metadata: 來自 scripts.json 的 Role_Data 區塊
        """
        self.metadata = role_metadata

    def _get_targets(self, actor, all_chars, target_logic, extra_params):
        """核心：目標選擇邏輯"""
        others_in_loc = [c for c in all_chars if c.location == actor.location and c != actor and not c.is_dead]
        
        if target_logic == "random_other_in_loc":
            return [random.choice(others_in_loc)] if others_in_loc else []
        
        elif target_logic == "all_others_in_loc":
            return others_in_loc
            
        elif target_logic == "vampire_logic":
            # 只有當現場剛好只有 2 人時觸發
            full_loc_list = [c for c in all_chars if c.location == actor.location and not c.is_dead]
            if len(full_loc_list) == 2:
                return [c for c in full_loc_list if c != actor]
            return []

        elif target_logic == "role_location":
            # 尋找特定角色的位置
            target_role = extra_params.get("target_role")
            target_char = next((c for c in all_chars if c.role == target_role and not c.is_dead), None)
            return [target_char] if target_char else []

        return []

    def _apply_effect(self, actor, target, effect_type, value, log_func):
        """核心：效果執行邏輯"""
        if effect_type == "kill":
            target.is_dead = True
            log_func(f"   🔪 {actor.name} 殺害了 {target.name}。")
            
        elif effect_type == "add_intrigue":
            if target.intrigue == 0:
                target.intrigue = 1
                log_func(f"   😈 {actor.name} 使 {target.name} 陷入陰謀。")
                
        elif effect_type == "sanity_damage":
            target.sanity -= value
            log_func(f"   🗣️ {actor.name} 的影響使 {target.name} 精神下降。")
            check_sanity_status(target, log_func)
            
        elif effect_type == "teleport":
            # 這裡的 target 其實是我們想要移動到的目標人物
            if actor.location != target.location:
                actor.location = target.location
                log_func(f"   🏃 {actor.name} 追蹤目標移動到了 Loc {target.location}。")

    def run(self, actor, all_chars, phase, log_func):
        """
        根據角色設定執行能力
        """
        if actor.is_dead: return
        
        config = self.metadata.get(actor.role)
        if not config or config["trigger"] != phase:
            return

        # 1. 獲取目標
        targets = self._get_targets(actor, all_chars, config["target"], config)
        
        # 2. 執行效果
        for t in targets:
            self._apply_effect(actor, t, config["effect"], config.get("value", 0), log_func)
