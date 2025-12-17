# gui_main.py
import tkinter as tk
from main import GameEngine
from settings import STATION_ID, SCRIPTS_DB # 載入修正後的 settings.py
from actions import ActionManager

class GameGUI(tk.Frame):
    def __init__(self, master=None):
        # ... 初始化 ...
        self.engine = GameEngine(logger_callback=self.log_message)
        # 關鍵：初始化控制器
        self.actions = ActionManager(self.engine) 
        # ... 
            
        # 載入動態地點名稱
        self.location_names = self._load_location_names()
        
        self.create_widgets()
        self.update_gui()
        self.log_message("\n--- 遊戲開始 ---")
        self.log_message(f"主劇本: {self.engine.scripts[0]['name']} | 支線: {self.engine.scripts[1]['name']}")

        
        
    def _load_location_names(self):
        """根據主劇本 ID 載入對應的地點名稱"""
        main_id = self.engine.scripts[0]['id']
        key = f"{main_id[0]}XX" # 例如 '111' 變成 '1XX'
        
        # 如果 JSON 裡沒有 Location_Names 區塊，提供預設值作為備用
        default_names = ["Loc 0", "Loc 1", "Loc 2", "Loc 3", "Loc 4"]
        
        return SCRIPTS_DB.get('Location_Names', {}).get(key, default_names)


    def create_widgets(self):
        # 狀態顯示區
        self.status_label = tk.Label(self, text="Status", anchor="w", justify="left")
        self.status_label.grid(row=0, column=0, columnspan=2, pady=10)

        # 日誌區
        self.log_text = tk.Text(self, width=80, height=15)
        self.log_text.grid(row=1, column=0, columnspan=2, padx=10)
        
        # 行動按鈕區
        self.action_frame = tk.Frame(self)
        self.action_frame.grid(row=2, column=0, pady=10)
        
        self.btn_next_phase = tk.Button(self.action_frame, text="回合結束 (AP: 0)", command=self.next_phase)
        self.btn_next_phase.pack(side="right", padx=5)

        # 動作按鈕 (假設玩家是第一個角色 self.engine.characters[0])
        self.current_char = self.engine.characters[0]
        
        self.move_buttons = []
        for i in range(5):
            name = self.location_names[i]
            btn = tk.Button(self.action_frame, text=f"移動到 {name} ({i})", command=lambda loc=i: self.action_move(loc))
            btn.pack(side="left", padx=2)
            self.move_buttons.append(btn)

        self.btn_ask = tk.Button(self.action_frame, text="詢問情報 (1 AP)", command=self.action_ask)
        self.btn_ask.pack(side="left", padx=5)
        
        # 繪製地圖/角色區
        self.map_canvas = tk.Canvas(self, width=600, height=300, bg='lightgray')
        self.map_canvas.grid(row=3, column=0, columnspan=2, pady=10)

    def log_message(self, message):
        """將日誌輸出到 Text Widget"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)


    def action_move(self, loc_id):
        # UI 只負責傳遞指令給 Controller
        success, message = self.actions.move(self.engine.characters[0], loc_id)
        self.log_message(message)
        self.update_gui()
        # 如果 AP 用完，自動提示可以點選結束回合 (或者自動結束)
        if self.engine.ap == 0:
            self.log_message("💡 AP 已耗盡，請結束回合。")

    def action_ask(self):
        success, message = self.actions.ask(self.engine.characters[0])
        self.log_message(message)
        self.update_gui()

    def next_phase(self):
        success, message = self.actions.end_turn()
        self.log_message(message)
        self.update_gui()

        super().__init__(master)
        self.master = master
        self.master.title("地下列車：多劇本測試版")
        self.pack()


    def update_gui(self):
        """更新所有 UI 資訊"""
        
        # 1. 更新狀態欄
        status = f"Day: {self.engine.day}/{self.engine.max_days} | AP: {self.engine.ap} | 墓碑: {len(self.engine.graves)}\n"
        status += f"你 ({self.current_char.name}, {self.current_char.role}) 所在 Loc: {self.current_char.location} ({self.location_names[self.current_char.location]})\n"
        status += f"精神: {self.current_char.sanity} | 陰謀: {self.current_char.intrigue}"
        
        self.status_label.config(text=status)
        
        # 2. 更新按鈕狀態
        can_act = self.engine.ap > 0 and not self.engine.is_game_over and not self.current_char.is_dead
        for btn in self.move_buttons:
            btn.config(state=tk.NORMAL if can_act else tk.DISABLED)
        self.btn_ask.config(state=tk.NORMAL if can_act else tk.DISABLED)
        self.btn_next_phase.config(state=tk.NORMAL if self.engine.ap == 0 and not self.engine.is_game_over else tk.DISABLED)

        # 3. 繪製地圖
        self._draw_map()

    def _draw_map(self):
        """在地圖畫布上繪製地點和人物"""
        self.map_canvas.delete("all")
        
        loc_positions = {
            0: (50, 100), 1: (150, 200), 2: (250, 100), 3: (350, 200), 4: (500, 150)
        }
        
        # [支線] 濃霧: 如果主劇本是客輪 (4XX) 且抽到濃霧， Loc 0 資訊模糊
        is_foggy = (self.engine.scripts[0]['id'][0] == '4' and self.engine.sub_rule == "thick_fog")
        
        # 繪製地點 (圈圈)
        for loc_id, (x, y) in loc_positions.items():
            name = self.location_names[loc_id]
            color = 'blue' if loc_id == STATION_ID else 'green'
            self.map_canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, outline='black')
            self.map_canvas.create_text(x, y+30, text=f"{loc_id}: {name}")
            
            # 繪製人物
            offset_y = -10
            chars_here = [c for c in self.engine.characters if c.location == loc_id and not c.is_dead]
            
            for i, char in enumerate(chars_here):
                
                # 判斷是否隱藏信息 (濃霧只隱藏 Loc 0 的信息)
                hide_info = is_foggy and loc_id == 0 and char != self.current_char

                char_text = char.name
                
                # 只有當人物不在濃霧中或人物是玩家自己時，才顯示完整信息
                if not hide_info or char == self.current_char:
                    # 顯示精神/陰謀/身份
                    char_info = f" S{char.sanity} I{char.intrigue} ({char.role})"
                    if char == self.current_char:
                        char_color = 'red' # 玩家自己
                    elif char.intrigue > 0:
                        char_color = 'purple'
                    elif char.sanity <= 1:
                        char_color = 'darkorange'
                    else:
                        char_color = 'black'
                else:
                    char_info = "(身份不明)"
                    char_color = 'gray' # 濃霧中的 NPC
                
                full_text = f"{char_text}{char_info}"
                
                self.map_canvas.create_text(x, y + offset_y + (i * 15), text=full_text, fill=char_color, anchor="center")

# 運行主程式
if __name__ == "__main__":
    root = tk.Tk()
    app = GameGUI(master=root)
    root.mainloop()

