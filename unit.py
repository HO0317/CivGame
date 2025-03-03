# unit.py

unit_stats = {
    "Swordsman": {"hp": 100, "attack": 20, "move": 1},
    "Archer": {"hp": 80, "attack": 25, "move": 1},
    "Mage": {"hp": 60, "attack": 30, "move": 1},
    "Spearman": {"hp": 90, "attack": 22, "move": 1},
    "Cavalry": {"hp": 110, "attack": 18, "move": 2},
}

strengths = {
    "Swordsman": "Archer",
    "Archer": "Mage",
    "Mage": "Spearman",
    "Spearman": "Cavalry",
    "Cavalry": "Swordsman",
}

class Unit:
    def __init__(self, unit_id, civ, unit_type, x, y, move_multiplier):
        self.id = unit_id
        self.civ = civ
        self.unit_type = unit_type
        self.x = x
        self.y = y
        self.hp = unit_stats[unit_type]['hp']
        self.attack = unit_stats[unit_type]['attack']
        self.base_move = unit_stats[unit_type]['move']
        self.remaining_move = self.base_move * move_multiplier
        self.move_order = None  # Next turn's destination (x, y)
