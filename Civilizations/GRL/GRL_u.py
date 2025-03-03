# GRL_u.py

def get_grl_unit_stats(unit_type):
    """
    Returns modified stats for Greenland-specific unit.
    For example, for "Inuit Warrior", increases hp by 20%, attack by 25%, and gives extra movement.
    """
    if unit_type == "Inuit Warrior":
        return {"hp": 120, "attack": 25, "move": 2}
    return None
