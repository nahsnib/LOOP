import random
from settings import STATION_ID, SCRIPTS_DB
from mechanics import process_arrival, calculate_sunrise_move, check_sanity_status
from scenario_gen import ScenarioBuilder
from abilities import AbilityEngine
from models import Grave

class GameEngine:
    def __init__(self, logger_callback=None):
        # 1. 基礎狀態初始化
        self.day = 1
        self.max_days = 4
        self.is_game_over = False
        self.graves = []
        self.ap = 5 
        self.blocked_locations = []  # 存儲目前被放置路障的地點 ID
        self.log_func = logger_callback if logger_callback else print

        # 2. 透過 Builder 初始化劇本與角色
        self.log("⚙️ 正在啟動劇本核心...")
        builder = ScenarioBuilder()
        self.characters, self.scripts = builder.build()
        
        # 3. 提取規則標籤 (用於後續勝敗判定)
        self.main_rule = self.scripts[0].get('rule_tag', 'default')
        self.sub_rule = self.scripts[1].get('rule_tag', 'default')
        self.foreshadow_data = self.scripts[2]
        
        # 4. 初始化能力引擎
        role_data = SCRIPTS_DB.get("Role_Data", {})
        self.ability_engine = AbilityEngine(role_data)
        
        self.log(f"📋 劇本加載成功：主線[{self.main_rule}] / 副線[{self.sub_rule}]")
        
        # 5. 劇本特殊規則初始化
        self._apply_initial_rules()

    def _apply_initial_rules(self):
        """根據劇本標籤進行初始調整"""
        if self.sub_rule == "masquerade":
            self.log("🎭 [規則] 假面舞會：所有人的性別已被隱藏。")
            for c in self.characters:
                c.gender = None 

        for c in self.characters:
            if c.role == "仿生人":
                c.sanity = 5 
        
        # 隨機分配一個初始陰謀
        if self.characters:
            target = random.choice(self.characters)
            target.intrigue = 1
            # self.log(f"DEBUG: 初始陰謀者是 {target.name}")

    def log(self, message):
        """將訊息輸出至介面"""
        if message:
            self.log_func(message)

    def _get_chars_in_loc(self, loc_id):
        """獲取特定地點的活人列表"""
        return [c for c in self.characters if c.location == loc_id and not c.is_dead]

    # --- 核心階段循環 ---

    def phase_sunrise(self):
        self.log("\n☀️ === 日出階段：角色能力發動 ===")
        # 每個日出，路障會失效（或者你可以自定義路障持續時間）
        if self.blocked_locations:
            self.log(f"🚧 地點 {self.blocked_locations} 的路障已拆除。")
            self.blocked_locations = []

        for c in self.characters:
            if not c.is_dead:
                self.ability_engine.run(c, self.characters, 'sunrise', self.log)

    def phase_morning(self):
        self.log(f"\n🏃 === 第 {self.day} 天 早上：NPC 移動 ===")
        
        # 副線規則：暴風雨
        if self.sub_rule == "stormy_seas" and random.random() < 0.5:
            self.log("🌊 暴風雨來襲，所有人受困原地無法移動！")
            return

        for c in self.characters:
            # 玩家(Index 0)不自動移動，死者不移動
            if c != self.characters[0] and not c.is_dead:
                # 傳入 blocked_locations，讓移動邏輯避開路障
                new_loc = calculate_sunrise_move(c.location, self.blocked_locations)
                if new_loc != c.location:
                    process_arrival(c, new_loc, self.log)

    def phase_dusk(self):
        self.log("\n🌅 === 黃昏階段：恐慌蔓延 ===")
        for c in self.characters:
            if not c.is_dead:
                self.ability_engine.run(c, self.characters, 'dusk', self.log)
        
        # 檢查黃昏伏筆
        self._check_events('dusk')

    def phase_night(self):
        self.log("\n🌃 === 夜晚階段：黑暗行動 ===")
        for c in self.characters:
            if not c.is_dead:
                self.ability_engine.run(c, self.characters, 'night', self.log)
        
        # 處理死亡與墓碑生成
        for c in self.characters:
            if c.is_dead and not any(g.name == c.name for g in self.graves):
                new_grave = Grave(c.name, c.location, self.day)
                self.graves.append(new_grave)
                self.log(f"⚰️ {c.name} 死亡，墓碑立於 {c.location}。")

        self._check_game_over()

    # --- 判定系統 ---

    def _check_events(self, phase):
        """觸發伏筆事件"""
        if phase == 'dusk':
            # 範例：如果有瘋子，觸發劇本定義的恐慌事件
            mad_chars = [c for c in self.characters if c.sanity <= 0 and not c.is_dead]
            if mad_chars and 'panic_event' in self.foreshadow_data:
                event = self.foreshadow_data['panic_event']
                self.log(f"📢 [事件] 恐慌觸發：{event['effect']}")
                # 執行具體效果邏輯...

    def _check_game_over(self):
        """檢查勝敗條件"""
        # 1. 死亡判定
        living_count = sum(1 for c in self.characters if not c.is_dead)
        if living_count <= 1:
            self.log("💀 倖存者過少，城市崩毀。遊戲結束。")
            self.is_game_over = True
            return

        # 2. 劇本特定判定 (範例：古老傳說-獻祭)
        if self.main_rule == "human_sacrifice" and len(self.graves) >= 6:
            self.log("💀 [結局] 獻祭已完成，古神甦醒。")
            self.is_game_over = True
            return

        # 3. 存活天數判定
        if self.day >= self.max_days:
            self.log("\n🎉 [勝利] 你成功存活到了第四天！")
            self.is_game_over = True
        else:
            self.day += 1
