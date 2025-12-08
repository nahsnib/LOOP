# models.py
from settings import STATION_ID

class Character:
    def __init__(self, id, name, default_loc, gender, sanity, forbidden):
        self.id = id
        self.name = name
        self.gender = gender
        self.location = default_loc
        
        # 數值狀態
        self.max_sanity = sanity
        self.sanity = sanity
        self.forbidden_region = forbidden
        
        # 隱藏資訊與標記
        self.role = "一般人"    
        self.intrigue = False   
        self.is_dead = False
        
        # 玩家互動
        self.guess_role = None  
        self.known = False      

    def __repr__(self):
        loc_str = "車站" if self.location == STATION_ID else f"Loc{self.location}"
        status = "💀" if self.is_dead else f"精{self.sanity}"
        face = "😈" if self.intrigue else ""
        role_display = ""
        if self.known: role_display = f" <真:{self.role}>"
        elif self.guess_role: role_display = f" [猜:{self.guess_role}?]"
        return f"[{self.name}({self.gender})|{loc_str}|{status}{face}]{role_display}"

class Grave:
    """墓碑物件，紀錄死亡資訊"""
    def __init__(self, location, char_name, day_of_death):
        self.location = location
        self.char_name = char_name
        self.day = day_of_death

    def __repr__(self):
        return f"[墓碑: {self.char_name} 歿於D{self.day} @Loc{self.location}]"