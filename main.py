# main.py
import time
import random
from settings import STATION_ID
from mechanics import process_arrival, calculate_sunrise_move, check_sanity_status
from scenario_gen import ScenarioBuilder
from abilities import ROLE_ABILITIES
from models import Grave

class GameEngine:
    def __init__(self, logger_callback=None):
        self.day = 1
        self.max_days = 4
        self.is_game_over = False
        self.graves = []
        self.ap = 5 
        self.log_func = logger_callback if logger_callback else print

        builder = ScenarioBuilder()
        self.characters, self.scripts = builder.build()
        
        self.main_rule = self.scripts[0].get('rule_tag', 'default')
        self.sub_rule = self.scripts[1].get('rule_tag', 'default')
        self.foreshadow_data = self.scripts[2]
        
        self.log(f"📋 劇本構築完成 (Rules: {self.main_rule} / {self.sub_rule})")
        
        # --- 劇本初始化處理 ---
        
        # 處理 "假面舞會" (性別屏蔽)
        if self.sub_rule == "masquerade":
            self.log("   🎭 假面舞會開始，所有人的性別變得模糊...")
            for c in self.characters:
                c.gender = None 

        # 處理 "仿生人" (給予高精神)
        for c in self.characters:
            if c.role == "仿生人":
                c.sanity = 5 
        
        self._assign_random_intrigue()
        self.ability_engine = AbilityEngine(SCRIPTS_DB.get("Role_Data", {}))
    def _execute_role_abilities(self, phase):
        """執行特定階段的角色能力 (現在統整為一個入口)"""
        self.log(f"   👤 處理 {phase} 階段角色能力...")
        for c in self.characters:
            self.ability_engine.run(c, self.characters, phase, self.log)

    def log(self, message):
        """通用日誌輸出"""
        self.log_func(message)

    def _assign_random_intrigue(self):
        """在遊戲開始時隨機分配陰謀狀態給一位人物"""
        if self.characters:
            target = random.choice(self.characters)
            target.intrigue = 1
            self.log(f"   👁️ 遊戲初始：{target.name} 被黑暗勢力盯上。")

    def _get_chars_in_loc(self, loc_id):
        """獲取特定地點的存活人物列表"""
        return [c for c in self.characters if c.location == loc_id and not c.is_dead]
        
    def _apply_event_effect(self, effect_type, loc_id, victim_name=None):
        """執行伏筆效果"""
        chars_in_zone = self._get_chars_in_loc(loc_id)
        
        # --- 擴充效果庫 ---
        if effect_type in ["spread_insanity", "toxic_gas"]: # 毒氣/恐慌
            msg = "陷入恐慌 (全員精神-1)" if effect_type == "spread_insanity" else "瀰漫神經毒素 (精神-2)"
            dmg = 1 if effect_type == "spread_insanity" else 2
            self.log(f"   🌀 [效果] Loc{loc_id} {msg}")
            for c in chars_in_zone:
                c.sanity -= dmg
                check_sanity_status(c, self.log_func)
                
            # [劇本3] 認知崩壞: 恐慌擴散至鄰區
            if self.sub_rule == "cognitive_collapse":
                self.log("   🧠 [連鎖] 認知崩壞導致恐慌擴散至相鄰區域！")
                # 假設 Loc 0, 1, 2, 3 兩兩相鄰，Loc 4 (車站) 連接到所有 0, 1, 2, 3
                neighbors = []
                if loc_id == STATION_ID: neighbors = [0, 1, 2, 3] # 車站擴散至全城
                elif loc_id in [0, 1, 2, 3]: neighbors = [(loc_id - 1)%4, (loc_id + 1)%4, STATION_ID] # 一般區域擴散至兩邊及車站
                
                for n_id in set(neighbors):
                    for nc in self._get_chars_in_loc(n_id):
                        if nc not in chars_in_zone: # 避免對同一區域重複扣除
                            nc.sanity -= 1
                            check_sanity_status(nc, self.log_func)

        elif effect_type == "riot":
            self.log(f"   🔥 [效果] Loc{loc_id} 發生暴動 (驅離)")
            for c in chars_in_zone:
                c.sanity -= 1
                new_loc = (c.location + random.choice([-1, 1])) % 4
                if c.location == STATION_ID: new_loc = random.randint(0, 3)
                c.location = new_loc
                check_sanity_status(c, self.log_func)

        elif effect_type == "random_teleport": # 劇本3
            self.log(f"   🤖 [效果] 系統錯誤，Loc{loc_id} 人員被隨機傳送！")
            for c in chars_in_zone:
                c.location = random.randint(0, 3)

        elif effect_type == "suicide":
            self.log(f"   ⚰️ [效果] {victim_name} 自我了斷。")
            victim = next((c for c in chars_in_zone if c.name == victim_name), None)
            if victim: victim.is_dead = True

        elif effect_type == "kill_one": # 劇本4
            if chars_in_zone:
                victim = random.choice(chars_in_zone)
                self.log(f"   🩸 [效果] 混亂中 {victim.name} 不幸身亡。")
                victim.is_dead = True

        elif effect_type == "massacre":
            self.log(f"   🩸 [效果] Loc{loc_id} 發生大屠殺 (全滅)。")
            for c in chars_in_zone: c.is_dead = True

        elif effect_type == "defeat":
            self.log(f"   💀 [效果] 觸發了毀滅性結局。")
            self.is_game_over = True

    def _check_foreshadowing_events(self, phase):
        """檢查伏筆是否觸發"""
        if phase == 'dusk':
            # 恐慌事件：檢查精神崩潰者
            mad_chars = [c for c in self.characters if c.sanity <= 0 and not c.is_dead]
            if mad_chars:
                event_data = self.foreshadow_data['panic_event']
                loc_id = event_data['loc']
                victim_name = mad_chars[0].name 
                
                self.log(f"\n📢 【恐慌伏筆】觸發：{event_data['name']}")
                self._apply_event_effect(event_data['effect'], loc_id, victim_name)

        elif phase == 'night':
            # 陰謀事件：檢查黑幕/邪教徒/陰謀者
            intrigue_chars = [c for c in self.characters if c.intrigue > 0 and not c.is_dead]
            # 僅在有特定身份的陰謀者存活時觸發
            mastermind_exists = any(c.role in ["黑幕", "邪教徒", "恐怖份子", "帶原者", "吸血鬼", "私生子"] for c in intrigue_chars)
            
            if intrigue_chars and mastermind_exists:
                event_data = self.foreshadow_data['intrigue_event']
                loc_id = event_data['loc']
                
                self.log(f"\n😈 【陰謀伏筆】觸發：{event_data['name']}")
                self._apply_event_effect(event_data['effect'], loc_id)
            
    def _check_game_over(self):
        """檢查所有劇本的勝敗條件"""
        
        # === 通用敗北條件 ===
        if sum(1 for c in self.characters if c.is_dead) >= len(self.characters):
             self.log("💀 全員死亡。"); self.is_game_over = True; return

        # === 劇本 1 (古老傳說) ===
        if self.main_rule == "human_sacrifice" and len(self.graves) >= 6:
            self.log("💀 【敗北】獻祭完成 (墓碑>=6)。"); self.is_game_over = True; return
        
        if self.main_rule == "secret_altar":
            loc_counts = {}
            for g in self.graves: loc_counts[g.location] = loc_counts.get(g.location, 0) + 1
            if any(c >= 3 for c in loc_counts.values()):
                self.log("💀 【敗北】神壇築起 (單區墓碑>=3)。"); self.is_game_over = True; return
        
        if self.main_rule == "evil_festival":
            if sum(1 for c in self.characters if not c.is_dead and c.intrigue > 0) > 4:
                self.log("💀 【敗北】惡意瀰漫 (陰謀者>4)。"); self.is_game_over = True; return

        # === 劇本 2 (現代都市) ===
        if self.main_rule == "graves_limit_strict" and len(self.graves) > 3:
            self.log("💀 【敗北】血流成河 (墓碑>3)。"); self.is_game_over = True; return
        
        if self.main_rule == "station_limit" and len(self._get_chars_in_loc(STATION_ID)) > 3:
            self.log("💀 【敗北】車站過載。"); self.is_game_over = True; return

        # === 劇本 3 (廢棄研究所 - Sci-Fi) ===
        if self.main_rule == "biohazard":
            mad_count = sum(1 for c in self.characters if not c.is_dead and c.sanity <= 0)
            if mad_count >= 3:
                self.log(f"💀 【敗北】生化汙染擴散 (崩潰者 {mad_count} >= 3)。"); self.is_game_over = True; return
        
        if self.main_rule == "ai_awakening":
            android = next((c for c in self.characters if c.role == "仿生人"), None)
            if android and not android.is_dead and android.intrigue > 0:
                self.log("💀 【敗北】AI 覺醒並反叛人類。"); self.is_game_over = True; return

        if self.main_rule == "reactor_meltdown":
            # 假設 Loc 2 是都市/反應爐
            if len(self._get_chars_in_loc(2)) == 0:
                self.log("💀 【敗北】反應爐無人監控，爐心熔毀。"); self.is_game_over = True; return

        # === 劇本 4 (豪華客輪 - Mystery) ===
        if self.main_rule == "vampire_hunt":
            vampire = next((c for c in self.characters if c.role == "吸血鬼"), None)
            if vampire and not vampire.is_dead and len(self.graves) > 4:
                self.log("💀 【敗北】吸血鬼飽餐一頓 (存活且墓碑>4)。"); self.is_game_over = True; return

        if self.main_rule == "succession_war":
            rich = next((c for c in self.characters if c.role == "富豪"), None)
            if rich and rich.is_dead: 
                self.log("💀 【敗北】富豪死亡，遺產爭奪戰失控。"); self.is_game_over = True; return

        if self.main_rule == "ghost_ship":
            # 檢查車站是否有墓碑
            if any(g.location == STATION_ID for g in self.graves):
                self.log("💀 【敗北】駕駛台(車站)被怨靈佔據。"); self.is_game_over = True; return
        
        # === 勝利條件 ===
        if self.day >= self.max_days:
            self.log("\n🎉 存活至期限！勝利！"); self.is_game_over = True
        else:
            self.day += 1

    def _check_special_rule_night(self):
        """檢查需要在夜晚階段額外判定的規則"""
        
        # 大樓爆破 (劇本2)
        if self.main_rule == "no_empty_zone":
            for i in range(4): # 檢查 Loc 0, 1, 2, 3
                if len(self._get_chars_in_loc(i)) == 0:
                    self.log(f"💀 【敗北】區域 {i} 無人 (大樓爆破)。"); self.is_game_over = True; return

    def _execute_role_abilities(self, phase):
        """執行特定階段的角色能力"""
        self.log(f"   👤 執行 {phase} 角色能力...")
        for c in self.characters:
            if not c.is_dead and c.role in ROLE_ABILITIES and phase in ROLE_ABILITIES[c.role]:
                ROLE_ABILITIES[c.role][phase](c, self.characters, self.log_func)

    def _process_intrigue_spread(self):
        """處理陰謀蔓延和解除"""
        new_intrigue_count = 0
        for c in self.characters:
            if c.intrigue > 0 and not c.is_dead:
                # 陰謀蔓延：每晚有 20% 機會讓周圍的人獲得陰謀
                neighbors = [c_n for c_n in self.characters if c_n.location == c.location and c_n != c and not c_n.is_dead]
                if neighbors and random.random() < 0.2:
                    target = random.choice(neighbors)
                    if target.intrigue == 0:
                        target.intrigue = 1
                        self.log(f"   😈 陰謀蔓延至 {target.name}。")
                new_intrigue_count += 1
        
        # 陰謀解除：每晚有 10% 機會解除一個陰謀
        if new_intrigue_count > 0 and random.random() < 0.1:
            intriguing_chars = [c for c in self.characters if c.intrigue > 0]
            target = random.choice(intriguing_chars)
            target.intrigue = 0
            self.log(f"   😇 {target.name} 的陰謀狀態被解除。")

    def phase_sunrise(self):
        """日出：邪教徒能力、戀人移動"""
        self.log("\n☀️ === 日出階段：角色特殊移動/能力 ===")
        self._execute_role_abilities('sunrise')

    def phase_morning(self):
        """早上：自動移動 (非車站人物)"""
        self.log(f"\n🏃 === Day {self.day}：早上自動移動 ===")
        
        # [劇本4] 暴風雨: 50% 機率無法移動
        skip_move = False
        if self.sub_rule == "stormy_seas" and random.random() < 0.5:
            self.log("   🌊 暴風雨太大了，船隻無法航行！(跳過移動)")
            skip_move = True

        if not skip_move:
            for c in self.characters:
                if c.location != STATION_ID and not c.is_dead:
                    new_loc = calculate_sunrise_move(c.location)
                    process_arrival(c, new_loc, self.log_func)
                    
                    # [劇本1] 譫妄病毒: 進入車站扣精神
                    if new_loc == STATION_ID and self.sub_rule == "virus_station":
                         self.log(f"   🦠 [病毒] {c.name} 進入車站 (-1 Sanity)")
                         c.sanity -= 1
                         check_sanity_status(c, self.log_func)

    def phase_noon(self):
        """中午：玩家行動階段 (AP 消耗)"""
        self.log("\n⏳ === 中午階段：玩家行動 ===")
        self.ap = 5 

    def phase_dusk(self):
        """黃昏：煽動者/黑幕能力、恐慌事件"""
        self.log("\n🌅 === 黃昏階段：恐慌蔓延 ===")
        self._execute_role_abilities('dusk')
        self._check_foreshadowing_events('dusk')

    def phase_night(self):
        """夜晚：殺手行動、陰謀事件、遊戲結束檢查"""
        self.log("\n🌃 === 夜晚階段：黑暗行動 ===")
        self._execute_role_abilities('night')
        self._process_intrigue_spread()
        self._check_foreshadowing_events('night')
        self._check_special_rule_night()

        # 處理死亡並生成墓碑
        dead_this_night = [c for c in self.characters if c.is_dead and c.name not in [g.name for g in self.graves]]
        for c in dead_this_night:
            self.graves.append(Grave(c.name, c.location, self.day))
            self.log(f"   ⚰️ {c.name} 死亡，墓碑立於 Loc {c.location}。")

        self._check_game_over()
        
    def step(self):
        """遊戲階段推進"""
        if self.is_game_over:
            return

        if self.day == 1 and self.ap == 5:
            # 第一天不執行日出/早上移動
            pass
        elif self.ap == 5:
            self.phase_sunrise()
            if self.is_game_over: return
            self.phase_morning()
            if self.is_game_over: return

        if self.ap > 0:
            self.phase_noon()
            # 玩家行動在 GUI 處理

        if self.ap == 0:
            self.phase_dusk()
            if self.is_game_over: return
            self.phase_night()
            
            # 若遊戲結束，將 AP 重置為 -1 停止迴圈
            if self.is_game_over:
                self.ap = -1
            else:
                self.ap = 5
