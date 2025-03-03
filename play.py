# play.py
import pygame
import random
from civ import Civilization, INITIAL_POPULATION
from unit import Unit, unit_stats, strengths
from building import RESIDENCE_POP_INCREASE, BARRACKS_TRAIN_COST

MOVE_MULTIPLIER = 3
MAIN_TILE_SIZE = 48   # Enlarged tile size
INFO_PANEL_HEIGHT = 100
MINIMAP_SCALE = 1.0

PLAYER_UNIT_COLOR = (255, 0, 0)
AI_UNIT_COLOR = (0, 0, 255)
WATER_COLOR = (50, 150, 255)

TILE_COLORS = {
    "Af (Tropical Rainforest)": (0, 155, 0),
    "Am (Tropical Monsoon)": (34, 200, 34),
    "Aw (Tropical Savanna)": (194, 178, 128),
    "BWh (Hot Desert)": (237, 201, 175),
    "BSh (Hot Semi-Arid)": (250, 222, 180),
    "BWk (Cold Desert)": (240, 230, 210),
    "BSk (Cold Semi-Arid)": (205, 133, 63),
    "Cfa (Humid Subtropical)": (60, 179, 113),
    "Cfb (Oceanic)": (176, 224, 230),
    "Csa (Hot-Summer Mediterranean)": (250, 214, 165),
    "Csb (Warm-Summer Mediterranean)": (255, 230, 200),
    "Cwa (Monsoon-influenced Humid Subtropical)": (80, 200, 100),
    "Dfa (Hot Summer Continental)": (220, 190, 160),
    "Dfb (Warm Summer Continental)": (210, 180, 150),
    "Dfc (Subarctic)": (180, 180, 210),
    "ET (Tundra)": (200, 220, 240),
    "EF (Ice Cap)": (240, 248, 255),
    "H (Highland)": (160, 160, 160),
    "As (Tropical Semi-arid)": (100, 180, 100),
    "Temperate Continental": (222, 184, 135),
    "Humid Subtropical": (60, 179, 113)
}

CLIMATE_ABBREV = {
    "Af (Tropical Rainforest)": "Af",
    "Am (Tropical Monsoon)": "Am",
    "Aw (Tropical Savanna)": "Aw",
    "BWh (Hot Desert)": "BWh",
    "BSh (Hot Semi-Arid)": "BSh",
    "BWk (Cold Desert)": "BWk",
    "BSk (Cold Semi-Arid)": "BSk",
    "Cfa (Humid Subtropical)": "Cfa",
    "Cfb (Oceanic)": "Cfb",
    "Csa (Hot-Summer Mediterranean)": "Csa",
    "Csb (Warm-Summer Mediterranean)": "Csb",
    "Cwa (Monsoon-influenced Humid Subtropical)": "Cwa",
    "Dfa (Hot Summer Continental)": "Dfa",
    "Dfb (Warm Summer Continental)": "Dfb",
    "Dfc (Subarctic)": "Dfc",
    "ET (Tundra)": "ET",
    "EF (Ice Cap)": "EF",
    "H (Highland)": "H",
    "As (Tropical Semi-arid)": "As",
    "Temperate Continental": "TC",
    "Humid Subtropical": "HS"
}

class Tile:
    def __init__(self, x, y, climate):
        self.x = x
        self.y = y
        self.climate = climate
        self.owner = None
        self.building = None  # "Capital", "Residence", "Barracks", "Igluvijaq", or None
        self.units = []

class Game:
    def __init__(self, grid_width, grid_height, civ_names, climate_grid, land_mask):
        self.full_width = grid_width
        self.full_height = grid_height
        self.turn = 0
        self.unit_counter = 0
        self.civs = []
        self.map = [[None for _ in range(self.full_width)] for _ in range(self.full_height)]
        self.climate_grid = climate_grid
        self.land_mask = land_mask
        self.init_map()
        self.init_civs(civ_names)
        self.season = self.get_player_season()

    def init_map(self):
        for y in range(self.full_height):
            for x in range(self.full_width):
                if self.land_mask[y][x]:
                    climate = self.climate_grid[y][x]
                    if climate is None or climate == "Unknown":
                        lat = 90 - (y / self.full_height) * 180
                        if lat >= 66.5 or lat <= -66.5:
                            climate = "EF (Ice Cap)"
                        elif -23.5 <= lat <= 23.5:
                            climate = "Af (Tropical Rainforest)"
                        elif 23.5 < lat < 45:
                            climate = "Dfb (Warm Summer Continental)"
                        else:
                            climate = "Humid Subtropical"
                    self.map[y][x] = Tile(x, y, climate)
                else:
                    self.map[y][x] = None

    def init_civs(self, civ_names):
        traits_list = [{} for _ in civ_names]
        random.shuffle(traits_list)
        for i, name in enumerate(civ_names):
            is_human = (i == 0)
            civ = Civilization(name, traits_list[i], is_human)
            self.civs.append(civ)
            civ.population = INITIAL_POPULATION
            civ.residences = 0
            civ.barracks = 0
            placed = False
            attempts = 0
            while not placed and attempts < 1000:
                x = random.randint(0, self.full_width - 1)
                y = random.randint(0, self.full_height - 1)
                tile = self.map[y][x]
                if tile is not None and tile.owner is None:
                    tile.owner = civ
                    civ.territory.add((x, y))
                    civ.capital = (x, y)
                    tile.building = "Capital"
                    new_unit = self.create_unit(civ, random.choice(list(unit_stats.keys())), x, y)
                    tile.units.append(new_unit)
                    civ.units.append(new_unit)
                    placed = True
                attempts += 1
            if civ.capital:
                cx, cy = civ.capital
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < self.full_width and 0 <= ny < self.full_height:
                            tile = self.map[ny][nx]
                            if tile is not None and tile.owner is None:
                                tile.owner = civ
                                civ.territory.add((nx, ny))

    def create_unit(self, civ, unit_type, x, y):
        self.unit_counter += 1
        return Unit(self.unit_counter, civ, unit_type, x, y, MOVE_MULTIPLIER)

    def get_player_season(self):
        capital = self.civs[0].capital
        if capital is None:
            return "Unknown"
        cx, cy = capital
        lat = 90 - (cy / self.full_height) * 180  # positive: northern; negative: southern
        capital_climate = self.map[cy][cx].climate
        turn_in_cycle = self.turn % 60
        if capital_climate and capital_climate.startswith("A"):
            if lat >= 0:
                return "Dry Season" if turn_in_cycle < 30 else "Wet Season"
            else:
                return "Wet Season" if turn_in_cycle < 30 else "Dry Season"
        else:
            if lat >= 0:
                if turn_in_cycle < 15:
                    return "Winter"
                elif turn_in_cycle < 30:
                    return "Spring"
                elif turn_in_cycle < 45:
                    return "Summer"
                else:
                    return "Autumn"
            else:
                if turn_in_cycle < 15:
                    return "Summer"
                elif turn_in_cycle < 30:
                    return "Autumn"
                elif turn_in_cycle < 45:
                    return "Winter"
                else:
                    return "Spring"

    def update_season(self):
        for civ in self.civs:
            if civ.is_human:
                for unit in civ.units:
                    unit.remaining_move = unit.base_move * MOVE_MULTIPLIER
        self.season = self.get_player_season()

    def get_effective_move(self, unit):
        base = unit.base_move * MOVE_MULTIPLIER
        current_tile = self.map[unit.y][unit.x]
        if unit.civ.name == "Greenland":
            if current_tile and current_tile.climate in ["ET (Tundra)", "EF (Ice Cap)"]:
                return int(base * 1.25)
            elif current_tile and current_tile.climate and (current_tile.climate.startswith("B") or current_tile.climate.startswith("Aw")):
                return int(base * 0.75)
        return int(base)

    def move_selected_unit(self, selected_unit, target_x, target_y):
        sx, sy = selected_unit.x, selected_unit.y
        effective_move = self.get_effective_move(selected_unit)
        distance = abs(target_x - sx) + abs(target_y - sy)
        if distance <= effective_move:
            selected_unit.move_order = (target_x, target_y)
        else:
            print("Target tile is out of reach.")

    def combat(self, attacker, defender):
        damage = attacker.attack * (1.5 if strengths.get(attacker.unit_type) == defender.unit_type else 1.0)
        attacker_tile = self.map[attacker.y][attacker.x]
        if attacker.civ.name == "Greenland" and attacker_tile and attacker_tile.climate in ["ET (Tundra)", "EF (Ice Cap)"]:
            damage *= 1.2
        defender.hp -= damage
        attacker.hp -= defender.attack
        print(f"{attacker.unit_type} attacked {defender.unit_type} for {damage:.1f} damage. Defender HP: {defender.hp}")
        print(f"Defender counter-attacked! Attacker HP: {attacker.hp}")

    def conquer_tile(self, civ, tile):
        old_owner = tile.owner
        tile.owner = civ
        civ.territory.add((tile.x, tile.y))
        if old_owner:
            old_owner.territory.discard((tile.x, tile.y))
            if (tile.x, tile.y) == old_owner.capital:
                self.eliminate_civ(old_owner, civ)

    def build_building(self, building_type, x, y, civ):
        tile = self.map[y][x]
        if tile is None:
            print("Cannot build on sea.")
            return
        if tile.owner != civ:
            print("This tile is not in your territory.")
            return
        if tile.building is not None:
            print("A building already exists here.")
            return
        if building_type == "Capital":
            print("Capital already exists for your country.")
            return
        elif building_type == "Residence":
            tile.building = "Residence"
            civ.population += RESIDENCE_POP_INCREASE
            civ.residences += 1
        elif building_type == "Barracks":
            tile.building = "Barracks"
            civ.barracks += 1
        elif building_type == "Igluvijaq":
            if tile.climate not in ["ET (Tundra)", "EF (Ice Cap)"]:
                print("Igluvijaq can only be built in cold climates (Tundra or Ice Cap).")
                return
            tile.building = "Igluvijaq"
            print(f"{civ.name} built Igluvijaq at ({x}, {y}).")
            return
        else:
            print("Invalid building type.")
            return
        print(f"{civ.name} built a {building_type} at ({x}, {y}).")

    def eliminate_civ(self, civ, conqueror):
        civ.alive = False
        for (x, y) in civ.territory:
            tile = self.map[y][x]
            if tile is not None:
                tile.owner = conqueror
                conqueror.territory.add((x, y))
        civ.territory.clear()
        for unit in list(civ.units):
            if unit in self.map[unit.y][unit.x].units:
                self.map[unit.y][unit.x].units.remove(unit)
            civ.units.remove(unit)

    def train_unit_from_barracks(self, x, y, civ):
        tile = self.map[y][x]
        if tile is None or tile.building != "Barracks":
            print("No barracks on this tile.")
            return
        if civ.population < BARRACKS_TRAIN_COST:
            print("Not enough population to train a unit.")
            return
        civ.population -= BARRACKS_TRAIN_COST
        new_unit = self.create_unit(civ, random.choice(list(unit_stats.keys())), x, y)
        tile.units.append(new_unit)
        civ.units.append(new_unit)
        print(f"{civ.name} trained a new unit at barracks ({x}, {y}).")

    def update_surrounded_territory_group(self, civ):
        visited = [[False] * self.full_width for _ in range(self.full_height)]
        for y in range(1, self.full_height - 1):
            for x in range(1, self.full_width - 1):
                if not visited[y][x] and self.map[y][x] is not None and self.map[y][x].owner is None:
                    group = []
                    queue = [(x, y)]
                    enclosed = True
                    while queue:
                        cx, cy = queue.pop(0)
                        if visited[cy][cx]:
                            continue
                        visited[cy][cx] = True
                        group.append((cx, cy))
                        if cx == 0 or cy == 0 or cx == self.full_width - 1 or cy == self.full_height - 1:
                            enclosed = False
                        for dx, dy in [(0,-1), (0,1), (-1,0), (1,0)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < self.full_width and 0 <= ny < self.full_height:
                                neighbor = self.map[ny][nx]
                                if neighbor is None:
                                    enclosed = False
                                elif not visited[ny][nx]:
                                    if neighbor.owner is not None and neighbor.owner != civ:
                                        enclosed = False
                                    elif neighbor.owner is None:
                                        queue.append((nx, ny))
                    if enclosed:
                        for (gx, gy) in group:
                            tile = self.map[gy][gx]
                            if tile is not None:
                                tile.owner = civ
                                civ.territory.add((gx, gy))

    def ai_turn(self):
        for civ in self.civs:
            if not civ.alive or civ.is_human:
                continue
            for unit in list(civ.units):
                if unit.remaining_move > 0:
                    dx, dy = random.choice([(0,-1), (0,1), (-1,0), (1,0)])
                    new_x = unit.x + dx
                    new_y = unit.y + dy
                    if 0 <= new_x < self.full_width and 0 <= new_y < self.full_height:
                        target_tile = self.map[new_y][new_x]
                        if target_tile is not None:
                            self.map[unit.y][unit.x].units.remove(unit)
                            unit.x = new_x
                            unit.y = new_y
                            target_tile.units.append(unit)
                            unit.remaining_move = max(0, unit.remaining_move - 1)
            if civ.territory:
                tx, ty = random.choice(list(civ.territory))
                tile = self.map[ty][tx]
                if tile and tile.building is None:
                    tile.building = "Capital"
        for unit in [unit for unit in self.civs[0].units if unit.move_order is not None]:
            sx, sy = unit.x, unit.y
            dest = unit.move_order
            dest_tile = self.map[dest[1]][dest[0]]
            if dest_tile is not None and any(e for e in dest_tile.units if e.civ != unit.civ):
                defender = [e for e in dest_tile.units if e.civ != unit.civ][0]
                orig = (sx, sy)
                self.combat(unit, defender)
                if defender.hp > 0:
                    if unit in self.map[unit.y][unit.x].units:
                        self.map[unit.y][unit.x].units.remove(unit)
                    unit.x, unit.y = orig
                    self.map[orig[1]][orig[0]].units.append(unit)
                    unit.move_order = None
                    continue
            else:
                if dest[0] != sx:
                    step = 1 if dest[0] > sx else -1
                    for x in range(sx, dest[0] + step, step):
                        tile = self.map[sy][x]
                        if tile is not None and tile.owner is None:
                            tile.owner = unit.civ
                            unit.civ.territory.add((x, sy))
                if dest[1] != sy:
                    step = 1 if dest[1] > sy else -1
                    for y in range(sy, dest[1] + step, step):
                        tile = self.map[y][dest[0]]
                        if tile is not None and tile.owner is None:
                            tile.owner = unit.civ
                            unit.civ.territory.add((dest[0], y))
            self.map[unit.y][unit.x].units.remove(unit)
            unit.x, unit.y = dest
            self.map[unit.y][unit.x].units.append(unit)
            cost = abs(dest[0] - sx) + abs(dest[1] - sy)
            unit.remaining_move = max(0, unit.remaining_move - cost)
            unit.move_order = None
        for civ in self.civs:
            if civ.is_human:
                self.update_surrounded_territory_group(civ)
        self.turn += 1
        self.update_season()
        
    def draw_main_view(self, surface, tile_size, castle_img, debug_mode=False):
        visible_cols = surface.get_width() // tile_size
        visible_rows = surface.get_height() // tile_size
        player_unit = self.civs[0].units[0]
        cam_x = player_unit.x - visible_cols // 2
        cam_y = player_unit.y - visible_rows // 2
        cam_x = max(0, min(cam_x, self.full_width - visible_cols))
        cam_y = max(0, min(cam_y, self.full_height - visible_rows))
        for j in range(visible_rows):
            for i in range(visible_cols):
                world_x = cam_x + i
                world_y = cam_y + j
                rect = pygame.Rect(i * tile_size, j * tile_size, tile_size, tile_size)
                if 0 <= world_x < self.full_width and 0 <= world_y < self.full_height:
                    tile = self.map[world_y][world_x]
                    if tile is None:
                        pygame.draw.rect(surface, WATER_COLOR, rect)
                    else:
                        color = TILE_COLORS.get(tile.climate, (200, 200, 200))
                        pygame.draw.rect(surface, color, rect)
                        if tile.owner:
                            border_color = PLAYER_UNIT_COLOR if tile.owner.is_human else AI_UNIT_COLOR
                            pygame.draw.rect(surface, border_color, rect, 2)
                        else:
                            pygame.draw.rect(surface, (50, 50, 50), rect, 1)
                        if tile.building:
                            font_small = pygame.font.SysFont(None, tile_size)
                            b_txt = font_small.render(tile.building[0], True, (0, 0, 0))
                            surface.blit(b_txt, (rect.x, rect.y))
                        if tile.owner and (tile.x, tile.y) == tile.owner.capital:
                            if castle_img:
                                scaled_castle = pygame.transform.scale(castle_img, (tile_size, tile_size))
                                surface.blit(scaled_castle, (rect.x, rect.y))
                            else:
                                pygame.draw.rect(surface, (100,100,100), rect, 3)
                        if debug_mode and tile.climate:
                            debug_font = pygame.font.SysFont(None, 12)
                            txt_color = (0,0,0) if tile.climate in ["EF (Ice Cap)", "ET (Tundra)"] else (255,255,255)
                            abbrev = CLIMATE_ABBREV.get(tile.climate, tile.climate)
                            dbg_txt = debug_font.render(abbrev, True, txt_color)
                            surface.blit(dbg_txt, (rect.x+2, rect.y+2))
        return cam_x, cam_y, visible_cols, visible_rows

def draw_minimap(game, screen, mini_surface, mini_x, mini_y, camera_x, camera_y, vis_cols, vis_rows, flags=None):
    screen.blit(mini_surface, (mini_x, mini_y))
    cam_rect = pygame.Rect(mini_x + int(camera_x * MINIMAP_SCALE),
                           mini_y + int(camera_y * MINIMAP_SCALE),
                           int(vis_cols * MINIMAP_SCALE),
                           int(vis_rows * MINIMAP_SCALE))
    pygame.draw.rect(screen, (255, 255, 0), cam_rect, 2)
    if flags:
        for civ in game.civs:
            if civ.territory:
                xs = [x for (x, y) in civ.territory]
                ys = [y for (x, y) in civ.territory]
                min_x = min(xs)
                max_x = max(xs)
                min_y = min(ys)
                max_y = max(ys)
                rect = pygame.Rect(min_x * MINIMAP_SCALE, min_y * MINIMAP_SCALE,
                                   (max_x - min_x + 1) * MINIMAP_SCALE,
                                   (max_y - min_y + 1) * MINIMAP_SCALE)
                if civ.name in flags:
                    flag_img = flags[civ.name]
                    flag_scaled = pygame.transform.scale(flag_img, (rect.width, rect.height))
                    flag_scaled.set_alpha(100)
                    screen.blit(flag_scaled, (mini_x + rect.x, mini_y + rect.y))

