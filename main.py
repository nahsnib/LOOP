import random
from settings import STATION_ID
from mechanics import process_arrival, calculate_sunrise_move, check_sanity_status
from scenario_gen import ScenarioBuilder
from abilities import AbilityEngine  # 確保您已經建立了上一次對話中的 AbilityEngine
from models import Grave

class GameEngine:
    def __init__(self, logger_callback=None):
        self.day = 1
        self.max_days = 4
        self.is_game_over = False
        self.graves = []
        self.ap = 5 
        self.blocked_locations = [] # 存儲路障地點 ID
        self.log_func = logger_callback if logger_callback else print

        # 初始化劇本與角色
        builder = ScenarioBuilder()
        self.characters, self.scripts = builder.build()
        
        # 提取規則設定 (從 ScenarioBuilder 回傳的資料中)
        self.main_rule = self.scripts[0].get('rule_tag', 'default')
        self.sub_rule = self.scripts[1].get('rule_tag', 'default')
        self.foreshadow_data = self.scripts[2]
        
        # 初始化能力引擎 (讀取 scripts.json 中的 Role_Data)
        # 注意：這裡假設您的 ScenarioBuilder 會讀取並提供角色資料
        from settings import SCRIPTS_DB
        self.ability_engine = AbilityEngine(SCRIPTS_DB.get("Role_Data", {}))
        
        self.log(f"📋 劇本構築完成: {self.main_rule} / {self.sub_rule}")
        
        # --- 劇本特殊初始化 ---
        if self.sub_rule == "masquerade":
            self.log("🎭 假面舞會開始，性別已屏蔽...")
            for c in self.characters:
                c.gender = None 

        for c in self.characters:
            if c.role == "仿生人":
                c.sanity = 5 
        
        self._assign_random_intrigue()

    def log(self, message):
        """通用日誌輸出"""
        if message:
            self.log_func(message)

    def _assign_random_intrigue(self):
        """遊戲初始隨機分配一個陰謀"""
        if self.characters:
            target = random.choice(self.characters)
            target.intrigue = 1
            self.log(f"👁️ 初始陰謀已潛伏在某處...")

    def _get_chars_in_loc(self, loc_id):
        return [c for c in self.characters if c.location == loc_id and not c.is_dead]

    def _apply_event_effect(self, effect_type, loc_id, victim_name=None):
        """執行伏筆效果邏輯"""
        chars_in_zone = self._get_chars_in_loc(loc_id)
        
        if effect_type in ["spread_insanity", "toxic_gas"]:
            dmg = 1 if effect_type == "spread_insanity" else 2
            self.log(f"🌀 [效果] Loc {loc_id} 發生災難！")
            for c in chars_in_zone:
                c.sanity -= dmg
                check_sanity_status(c, self.log_func)

        elif effect_type == "massacre":
            self.log(f"🩸 [效果] Loc {loc_id} 發生大屠殺！")
            for c in chars_in_zone:
                c.is_dead = True

    def _check_foreshadowing_events(self, phase):
        """檢查伏筆事件觸發"""
        if phase == 'dusk':
            mad_chars = [c for c in self.characters if c.sanity <= 0 and not c.is_dead]
            if mad_chars:
                event = self.foreshadow_data.get('panic_event')
                if event:
                    self.log("\n📢 【恐慌伏筆】觸發！")
                    self._apply_event_effect(event['effect'], event['loc'], mad_chars[0].name)

    def _check_game_over(self):
        """勝敗判定"""
        # 通用死亡判定
        if sum(1 for c in self.characters if c.is_dead) >= len(self.characters):
            self.log("💀 全員死亡。遊戲結束。")
            self.is_game_over = True
            return

        # 勝利判定
        if self.day >= self.max_days:
            self.log("\n🎉 存活至期限！人類的勝利。")
            self.is_game_over = True
        else:
            self.day += 1

    def phase_sunrise(self):
        self.log("\n☀️ === 日出階段 ===")
        # 執行角色能力 (日出觸發)
        for c in self.characters:
            self.ability_engine.run(c, self.characters, 'sunrise', self.log)

    def phase_morning(self):
        self.log(f"\n🏃 === 第 {self.day} 天 早上：自動移動 ===")
        # 考慮暴風雨規則
        if self.sub_rule == "stormy_seas" and random.random() < 0.5:
            self.log("🌊 暴風雨影響，NPC 無法移動。")
            return

        for c in self.characters:
            # 玩家不自動移動，死者不移動
            if c != self.characters[0] and not c.is_dead:
                # 傳入路障列表
                new_loc = calculate_sunrise_move(c.location, self.blocked_locations)
                process_arrival(c, new_loc, self.log)

    def phase_dusk(self):
        self.log("\n🌅 === 黃昏階段 ===")
        for c in self.characters:
            self.ability_engine.run(c, self.characters, 'dusk', self.log)
        self._check_foreshadowing_events('dusk')

    def phase_night(self):
        self.log("\n🌃 === 夜晚階段 ===")
        for c in self.characters:
            self.ability_engine.run(c, self.characters, 'night', self.log)
        
        # 處理新死者生成墓碑
        for c in self.characters:
            if c.is_dead and not any(g.name == c.name for g in self.graves):
                self.graves.append(Grave(c.name, c.location, self.day))
                self.log(f"⚰️ {c.name} 的墓碑立於 Loc {c.location}")

        self._check_game_over()
