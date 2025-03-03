# civ.py
INITIAL_POPULATION = 1000

# "Greenland" civilization is handled internally as "GRL".
# In tundra climates, move rate is increased by 1.25; in tropical/arid climates (those starting with 'A' or 'B' or "Aw"),
# move rate is reduced to 0.75.
DEFAULT_GRL_TRAITS = {
    "ET (Tundra)": 1.25,
    "EF (Ice Cap)": 1.25,
    "BWh (Hot Desert)": 0.75,
    "BSh (Hot Semi-Arid)": 0.75,
    "Aw (Tropical Savanna)": 0.75
}

class Civilization:
    def __init__(self, name, traits=None, is_human=False):
        self.name = name  # Full name (e.g., "Greenland", "Aurelia", etc.)
        if name == "Greenland":
            self.internal_name = "GRL"  # For internal use (e.g., flag filename)
            self.traits = DEFAULT_GRL_TRAITS
        else:
            self.internal_name = name
            self.traits = traits if traits is not None else {}
        self.is_human = is_human
        self.units = []
        self.territory = set()  # Set of (x, y) coordinates
        self.capital = None     # (x, y) coordinate of capital
        self.alive = True
        self.population = INITIAL_POPULATION
        self.residences = 0
        self.barracks = 0
