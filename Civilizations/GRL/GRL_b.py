# GRL_b.py

def build_igluvijaq(civ, tile):
    """
    Builds the Greenland-specific building "Igluvijaq" on the given tile.
    It can only be built if tile.climate is either "ET (Tundra)" or "EF (Ice Cap)".
    """
    if tile.climate in ["ET (Tundra)", "EF (Ice Cap)"]:
        tile.building = "Igluvijaq"
        print(f"{civ.name} built Igluvijaq at ({tile.x}, {tile.y}).")
    else:
        print("Igluvijaq can only be built in cold climates (Tundra or Ice Cap).")
