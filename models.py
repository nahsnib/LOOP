# models.py
class Character:
    """遊戲中所有人物的屬性"""
    def __init__(self, name, gender, location, role="一般人", sanity=3):
        self.name = name
        self.gender = gender # F/M/None
        self.location = location # 0-4
        self.role = role
        self.sanity = sanity # 精神值 (0 觸發恐慌)
        self.intrigue = 0 # 陰謀值 (1 觸發陰謀)
        self.is_dead = False
        self.known = False # 玩家是否確認其身分

class Grave:
    """墓碑物件，用於記錄死亡位置和時間"""
    def __init__(self, name, location, day):
        self.name = name
        self.location = location
        self.day = day
