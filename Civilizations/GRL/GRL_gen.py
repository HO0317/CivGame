# Civilizations/GRL/GRL_gen.py
FULL_NAME = "Greenland"
PASSIVE_NAME = "Eskimo"
PASSIVE_DESC = "In cold climates, units gain increased movement and attack bonuses."
UNIQUE_UNIT = "Inuit Warrior"
UNIQUE_UNIT_DESC = "A fierce warrior adapted to harsh cold with enhanced combat skills in tundra environments."
UNIQUE_BUILDING = "Igluvijaq"
UNIQUE_BUILDING_DESC = "A special building that can be built in cold climates without population cost, providing extra defense."

class GreenlandGeneral:
    def __init__(self, is_human=False):
        self.name = FULL_NAME
        self.internal_name = "GRL"  # 반드시 문자열로 설정
        self.is_human = is_human
        self.passive_name = PASSIVE_NAME
        self.passive_desc = PASSIVE_DESC
        self.unique_unit = UNIQUE_UNIT
        self.unique_unit_desc = UNIQUE_UNIT_DESC
        self.unique_building = UNIQUE_BUILDING
        self.unique_building_desc = UNIQUE_BUILDING_DESC
