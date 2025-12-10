# main.py
import time
from settings import STATION_ID
from mechanics import process_arrival, calculate_sunrise_move, check_sanity_status
from scenario_gen import ScenarioBuilder
from abilities import ROLE_ABILITIES
from models import Grave

class GameEngine:
    def __init__(self, logger_callback=None):
        """
        logger_callback: 一個函數，接收字串參數。
        例如: gui.logger.log
        """
        self.day = 1
        self.max_days = 4
        self.is_game_over = False
        self.graves = []
        self.ap = 5 
        
        # 設定 Log 輸出目的地
        self.log_func = logger_callback if logger_callback else print

        builder = ScenarioBuilder()
        self.characters, self.scripts = builder.build()

    # 一個方便內部的 Log 方法
    def log(self, text):
        self.log_func(text)

    def _execute_role_abilities(self, phase_name):
        active_chars = [c for c in self.characters if not c.is_dead and c.location != STATION_ID]
        for char in active_chars:
            if char.role in ROLE_ABILITIES:
                abilities = ROLE_ABILITIES[char.role]
                if phase_name in abilities:
                    # 傳入 self.log_func 給技能使用
                    abilities[phase_name](char, self.characters, self.log_func)

    def _process_intrigue_spread(self):
        for region_id in range(4):
            chars = [c for c in self.characters if c.location != STATION_ID and c.location // 3 == region_id]
            if any(c.intrigue for c in chars):
                for c in chars:
                    if not c.intrigue:
                        self.log(f"   😈 {c.name} 看見了那抹笑容... (感染陰謀)")
                        c.intrigue = True
    
    def _update_graves(self):
        for char in self.characters:
            if char.is_dead and char.sanity <= 0:
                grave_exists = any(g.char_name == char.name for g in self.graves)
                if not grave_exists:
                    self.log(f"   🪦 已為 {char.name} 在 Loc{char.location} 設立墓碑。")
                    new_grave = Grave(char.location, char.name, self.day)
                    self.graves.append(new_grave)

    def _check_game_over(self):
        dead = sum(1 for c in self.characters if c.is_dead)
        insane = sum(1 for c in self.characters if c.sanity <= 0)
        
        if dead > 0 or insane > 0:
            self.log(f"\n💀 悲劇發生... (死亡:{dead}, 發狂:{insane})")
            self.is_game_over = True
        elif self.day >= self.max_days:
            self.log("\n🎉 存活至期限！勝利！(True End)")
            self.is_game_over = True
        else:
            self.day += 1

    # === 階段流程 (全部改用 self.log) ===
    def phase_sunrise(self):
        self.log(f"\n🌞 === Day {self.day}：日出 ===")
        for c in self.characters:
            if c.location == STATION_ID and not c.is_dead:
                self.log(f"   Station: {c.name} 在車站過夜，精神 -1")
                c.sanity -= 1
                check_sanity_status(c, self.log_func)

    def phase_morning(self):
        self.log(f"\n🏃 === Day {self.day}：早上自動移動 ===")
        for c in self.characters:
            if c.location != STATION_ID and not c.is_dead:
                new_loc = calculate_sunrise_move(c.location)
                # 傳入 log_func
                process_arrival(c, new_loc, self.log_func)

    def phase_noon(self):
        self.log(f"\n🤝 === Day {self.day}：中午玩家行動 ===")
        self.ap = 5
        self.log(f"   ⚡ 行動點數已重置為 {self.ap} 點")

    def phase_dusk(self):
        self.log(f"\n🌆 === Day {self.day}：黃昏 ===")
        self._execute_role_abilities("dusk")
        self._process_intrigue_spread()

    def phase_night(self):
        self.log(f"\n🌙 === Day {self.day}：夜間 ===")
        self._execute_role_abilities("night")
        self._update_graves()
        self._check_game_over()

if __name__ == "__main__":
    game = GameEngine()
    print("請執行 gui_main.py 進行遊玩")