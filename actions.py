# actions.py
import random

class ActionManager:
    def __init__(self, engine):
        """
        :param engine: 傳入 GameEngine 實例，以便讀取當前遊戲狀態 (AP, scripts, characters)
        """
        self.engine = engine

    def can_perform_action(self, char):
        """通用檢查：人物是否存活且還有行動點"""
        if char.is_dead:
            return False, "💀 您已經死亡，無法行動。"
        if self.engine.ap <= 0:
            return False, "🚫 行動點 (AP) 已耗盡。"
        if self.engine.is_game_over:
            return False, "🏁 遊戲已結束。"
        return True, ""

    def move(self, char, target_loc_id):
        """
        處理移動動作
        返回: (bool 成功與否, str 訊息回饋)
        """
        success, msg = self.can_perform_action(char)
        if not success: return False, msg

        # 1. 計算移動成本 (預設 1 AP)
        cost = 1
        
        # [劇本規則] 全域封鎖 (321): 進入隔離區 (Loc 1) 需 2 AP
        if self.engine.sub_rule == "lockdown" and target_loc_id == 1:
            cost = 2
            if self.engine.ap < cost:
                return False, "🚨 [封鎖] AP 不足 (進入隔離區需 2 AP)。"

        # [劇本規則] 監禁 (222): 所有移動 AP 消耗加倍
        if self.engine.sub_rule == "high_cost_move":
            cost *= 2
            if self.engine.ap < cost:
                return False, "⛓️ [監禁] 體力消耗劇增，AP 不足。"

        # 2. 執行移動
        char.location = target_loc_id
        self.engine.ap -= cost
        
        # 3. 觸發抵達邏輯 (從 mechanics 呼叫，但由 controller 統一控管)
        # 這裡我們甚至可以把 mechanics.process_arrival 的輸出捕獲回來
        return True, f"🏃 移動至 Loc {target_loc_id}，消耗 {cost} AP。"

    def ask(self, char):
        """
        處理詢問情報動作
        返回: (bool 成功與否, str 訊息回饋)
        """
        success, msg = self.can_perform_action(char)
        if not success: return False, msg

        # 1. 計算成本
        cost = 1
        # [劇本規則] 情報商 (223): 詢問僅需 0 AP (如果還有剩餘 AP)
        if self.engine.sub_rule == "cheap_ask":
            cost = 0

        # 2. 執行詢問邏輯
        loc_chars = [c for c in self.engine.characters if c.location == char.location and c != char and not c.is_dead]
        
        if loc_chars:
            target = random.choice(loc_chars)
            self.engine.ap -= cost
            # 標記目標為已知 (以便 UI 顯示真實身份)
            target.known = True 
            info = f"🕵️ 詢問 {target.name}: [身份:{target.role} | 精神:{target.sanity}]"
            return True, f"{info} (消耗 {cost} AP)"
        else:
            return False, "❓ 這裡沒有其他活人可以詢問。"

    def end_turn(self):
        """
        結束玩家階段，推進遊戲至黃昏與夜晚
        返回: (bool 成功與否, str 訊息回饋)
        """
        if self.engine.ap > 0:
            return False, "⚠️ 尚有 AP 未使用，無法結束回合。"
        
        if self.engine.is_game_over:
            return False, "🏁 遊戲已結束。"

        # 呼叫引擎執行後續階段
        self.engine.phase_dusk()
        if self.engine.is_game_over: return True, "🌅 黃昏結束，遊戲進入結局。"
        
        self.engine.phase_night()
        
        # 如果夜晚過後遊戲沒結束，準備新的一天
        if not self.engine.is_game_over:
            self.engine.phase_sunrise()
            self.engine.phase_morning()
            self.engine.ap = 5 
            return True, f"☀️ 新的一天開始 (Day {self.engine.day})。"
        
        return True, "🌃 夜晚結束。"
