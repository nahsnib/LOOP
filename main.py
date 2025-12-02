import random
import time

# ==========================================
# 1. 基礎資料結構 (Data Structures)
# ==========================================

class Character:
    def __init__(self, name, loc, forbidden, sanity, role="一般人"):
        self.name = name
        self.location = loc  # 0-11: 地圖, -1: 車站
        self.forbidden_region = forbidden # 0:神社, 1:醫院, 2:都市, 3:學校
        self.sanity = sanity
        self.max_sanity = sanity
        self.intrigue = False # 陰謀狀態 (笑臉)
        self.role = role      # 劇本身分 (殺手/散播者/一般人)
        self.is_dead = False

    def __repr__(self):
        # 視覺化輸出狀態
        loc_str = "車站" if self.location == -1 else f"Loc{self.location}"
        status = "💀" if self.is_dead else f"精{self.sanity}"
        face = "😈" if self.intrigue else "" 
        return f"[{self.name}|{loc_str}|{status}{face}|{self.role}]"

class GameEngine:
    def __init__(self):
        self.STATION = -1
        self.MAP_SIZE = 12
        self.day = 1
        self.max_days = 3 # 撐過第3天即勝利
        self.is_game_over = False
        self.characters = []
        
        # 建立第零號劇本的角色 (簡化版：4人)
        # 參數：姓名, 初始位置, 禁地(區域0-3), 初始精神, 身分
        self.characters.append(Character("巫女", 0, 2, 2, "一般人"))   # 禁地:都市
        self.characters.append(Character("醫生", 3, 0, 3, "散播者"))   # 禁地:神社
        self.characters.append(Character("警察", 6, 1, 3, "一般人"))   # 禁地:醫院
        self.characters.append(Character("學生", 9, 2, 2, "殺手"))     # 禁地:都市(假設)

    # ==========================================
    # 2. 核心移動邏輯 (Decoupled Movement Logic)
    # ==========================================
    
    def _process_arrival(self, char, new_location):
        """處理抵達邏輯：更新位置並檢查禁地"""
        char.location = new_location
        
        if new_location == self.STATION:
            return # 已經在車站，無需檢查

        region = new_location // 3
        if region == char.forbidden_region:
            print(f"   ⚠️  [警告] {char.name} 誤入禁地 (區域{region})！")
            self._send_to_station(char)

    def _send_to_station(self, char):
        """強制送入車站並扣精神"""
        print(f"   🛑 {char.name} 被轉移至車站，精神 -1")
        char.location = self.STATION
        self.modify_sanity(char, -1)

    def modify_sanity(self, char, amount):
        """統一處理精神變化，包含死亡/發狂檢查"""
        if char.is_dead: return
        char.sanity += amount
        if char.sanity <= 0:
            print(f"   😱 {char.name} 精神崩潰 (Sanity 0)！")
            # 在此劇本中，精神歸零視為敗北條件之一，或者容易導致死亡
            # 這裡暫時不直接致死，留給黃昏/夜間判斷

    # ==========================================
    # 3. 遊戲階段 (Game Phases)
    # ==========================================

    def phase_sunrise(self):
        print(f"\n🌞 === 第 {self.day} 天：日出 (Sunrise) ===")
        # [規則] 車站內角色 -1 精神 [cite: 36]
        for c in self.characters:
            if c.location == self.STATION and not c.is_dead:
                print(f"   Station: {c.name} 在車站過夜，精神 -1")
                self.modify_sanity(c, -1)

    def phase_morning(self):
        print(f"\n🏃 === 第 {self.day} 天：早上移動 (Morning) ===")
        # [規則] 全體逆時針移動 1 格，車站內除外 [cite: 64]
        for c in self.characters:
            if c.location != self.STATION and not c.is_dead:
                old_loc = c.location
                new_loc = (c.location - 1) % self.MAP_SIZE # 逆時針
                print(f"   Move: {c.name} 從 {old_loc} 移動到 {new_loc}")
                self._process_arrival(c, new_loc)

    def phase_noon(self):
        print(f"\n🤝 === 第 {self.day} 天：中午互動 (Noon) ===")
        print("當前盤面：")
        for c in self.characters: print(f"  {c}")
        
        # 簡單的互動迴圈 (MVP 僅開放一次行動以利測試)
        print("\n請選擇行動 (輸入指令):")
        print("1. swap [Name1] [Name2] (交換位置)")
        print("2. move [Name] [LocID] (移動出車站)")
        print("3. skip (跳過)")
        
        try:
            cmd = input(">> ").split()
            if not cmd: return
            
            if cmd[0] == "swap" and len(cmd) == 3:
                c1 = next((x for x in self.characters if x.name == cmd[1]), None)
                c2 = next((x for x in self.characters if x.name == cmd[2]), None)
                if c1 and c2:
                    print(f"   Action: 交換 {c1.name} 與 {c2.name}")
                    # 交換邏輯：先記錄目標位置，再分別 Process Arrival
                    loc1, loc2 = c1.location, c2.location
                    if loc1 == -1 or loc2 == -1:
                        print("   Error: 車站內無法交換")
                    else:
                        self._process_arrival(c1, loc2)
                        self._process_arrival(c2, loc1)
            
            elif cmd[0] == "move" and len(cmd) == 3:
                c1 = next((x for x in self.characters if x.name == cmd[1]), None)
                target = int(cmd[2])
                if c1 and c1.location == self.STATION:
                    # 檢查目標地是否有人 (MVP 簡化：假設沒人)
                    print(f"   Action: 將 {c1.name} 救出至 {target}")
                    self._process_arrival(c1, target)
                else:
                    print("   Error: 只能移動車站內的角色")

        except Exception as e:
            print(f"輸入錯誤: {e}")

    def phase_dusk(self):
        print(f"\n🌆 === 第 {self.day} 天：黃昏 (Dusk) ===")
        # [劇本邏輯] 散播者 (Spreader) 能力發動
        spreader = next((c for c in self.characters if c.role == "散播者"), None)
        if spreader and not spreader.is_dead and spreader.location != -1:
            region = spreader.location // 3
            print(f"   👿 散播者 {spreader.name} 在區域 {region} 散布恐懼！")
            for c in self.characters:
                if c.location != -1 and (c.location // 3) == region:
                    print(f"      -> {c.name} 精神 -1")
                    self.modify_sanity(c, -1)

        # [劇本邏輯] 陰謀傳染 (Infection)
        # 檢查每個區域，如果有人有陰謀(笑臉)，傳染給同區其他人
        for region_id in range(4):
            chars_in_region = [c for c in self.characters if c.location != -1 and c.location // 3 == region_id]
            has_intrigue = any(c.intrigue for c in chars_in_region)
            if has_intrigue:
                for c in chars_in_region:
                    if not c.intrigue:
                        print(f"   😈 {c.name} 被傳染了陰謀！(露出笑臉)")
                        c.intrigue = True

    def phase_night(self):
        print(f"\n🌙 === 第 {self.day} 天：夜間 (Night) ===")
        
        # [劇本邏輯] 殺手 (Killer) 行動
        killer = next((c for c in self.characters if c.role == "殺手"), None)
        if killer and not killer.is_dead and killer.location != -1:
            region = killer.location // 3
            # 找出同區域的受害者
            targets = [c for c in self.characters if c.location != -1 and (c.location // 3) == region and c != killer]
            
            # 殺手邏輯：如果該區只有自己，不動手；否則殺掉精神最低的
            if targets:
                target = min(targets, key=lambda x: x.sanity)
                print(f"   🔪 殺手 {killer.name} 殺害了 {target.name}！")
                target.is_dead = True
                target.sanity = 0

        # [勝負判定]
        # 1. 敗北：有人死亡 或 精神<=0
        dead_count = sum(1 for c in self.characters if c.is_dead)
        insane_count = sum(1 for c in self.characters if c.sanity <= 0)
        
        if dead_count > 0 or insane_count > 0:
            print(f"\n💀 遊戲結束：敗北！ (死亡:{dead_count}, 發狂:{insane_count})")
            self.is_game_over = True
            return

        # 2. 勝利：撐過最後一天
        if self.day >= self.max_days:
            print("\n🎉 遊戲結束：勝利！你成功阻止了悲劇。")
            self.is_game_over = True
            return

        # 推進日期
        self.day += 1

    def run(self):
        print("=== 遊戲開始：第零號劇本 ===")
        while not self.is_game_over:
            self.phase_sunrise()
            if self.is_game_over: break
            self.phase_morning()
            self.phase_noon()
            self.phase_dusk()
            self.phase_night()
            time.sleep(1) # 暫停一下讓玩家閱讀

# ==========================================
# 啟動遊戲
# ==========================================
if __name__ == "__main__":
    game = GameEngine()
    game.run()
