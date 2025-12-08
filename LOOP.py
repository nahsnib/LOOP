# main.py
import time
from settings import STATION_ID
from mechanics import process_arrival, calculate_sunrise_move, check_sanity_status
from scenario_gen import ScenarioBuilder
from abilities import ROLE_ABILITIES
from models import Grave

class GameEngine:
    def __init__(self):
        self.day = 1
        self.max_days = 4
        self.is_game_over = False
        self.graves = [] # 墓碑列表
        
        builder = ScenarioBuilder()
        self.characters, self.scripts = builder.build()

    def _execute_role_abilities(self, phase_name):
        active_chars = [c for c in self.characters if not c.is_dead and c.location != STATION_ID]
        for char in active_chars:
            if char.role in ROLE_ABILITIES:
                abilities = ROLE_ABILITIES[char.role]
                if phase_name in abilities:
                    abilities[phase_name](char, self.characters)

    def _process_intrigue_spread(self):
        for region_id in range(4):
            chars = [c for c in self.characters if c.location != STATION_ID and c.location // 3 == region_id]
            if any(c.intrigue for c in chars):
                for c in chars:
                    if not c.intrigue:
                        print(f"   😈 {c.name} 看見了那抹笑容... (感染陰謀)")
                        c.intrigue = True
    
    def _update_graves(self):
        """檢查死亡角色，為尚未立碑者設立墓碑"""
        for char in self.characters:
            if char.is_dead and char.sanity <= 0:
                grave_exists = any(g.char_name == char.name for g in self.graves)
                if not grave_exists:
                    print(f"   🪦 已為 {char.name} 在 Loc{char.location} 設立墓碑。")
                    new_grave = Grave(char.location, char.name, self.day)
                    self.graves.append(new_grave)

    def _check_game_over(self):
        dead = sum(1 for c in self.characters if c.is_dead)
        insane = sum(1 for c in self.characters if c.sanity <= 0)
        
        if dead > 0 or insane > 0:
            print(f"\n💀 悲劇發生... (死亡:{dead}, 發狂:{insane})")
            self.is_game_over = True
        elif self.day >= self.max_days:
            print("\n🎉 存活至期限！勝利！(True End)")
            self.is_game_over = True
        else:
            self.day += 1

    # === 階段流程 ===
    def phase_sunrise(self):
        print(f"\n🌞 === Day {self.day}：日出 ===")
        for c in self.characters:
            if c.location == STATION_ID and not c.is_dead:
                print(f"   Station: {c.name} 在車站過夜，精神 -1")
                c.sanity -= 1
                check_sanity_status(c)

    def phase_morning(self):
        print(f"\n🏃 === Day {self.day}：早上自動移動 ===")
        for c in self.characters:
            if c.location != STATION_ID and not c.is_dead:
                new_loc = calculate_sunrise_move(c.location)
                process_arrival(c, new_loc)

    def phase_noon(self):
        print(f"\n🤝 === Day {self.day}：中午玩家行動 (等待GUI操作) ===")

    def phase_dusk(self):
        print(f"\n🌆 === Day {self.day}：黃昏 ===")
        self._execute_role_abilities("dusk")
        self._process_intrigue_spread()

    def phase_night(self):
        print(f"\n🌙 === Day {self.day}：夜間 ===")
        self._execute_role_abilities("night")
        self._update_graves() # 立碑
        self._check_game_over()

    def trigger_final_battle(self):
        # 僅供文字版使用，GUI版有自己的邏輯
        pass

if __name__ == "__main__":
    game = GameEngine()
    print("請執行 gui_main.py 進行遊玩")