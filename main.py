import pygame
import sys
import os
import numpy as np
import rasterio
from map_ import load_map_data, create_minimap_surface
from play import Game, draw_minimap, MAIN_TILE_SIZE, INFO_PANEL_HEIGHT, MOVE_MULTIPLIER, PLAYER_UNIT_COLOR, AI_UNIT_COLOR
from building import building_menu

# 기본 상수 (영어 인터페이스)
DEFAULT_AI_NAME = "Base_Civ"
DEFAULT_AI_FLAG = "Base_Civ_circle.png"
FLAG_MAPPING = {
    "GRL": "GRL_circle.png",
    "Base_Civ": DEFAULT_AI_FLAG
}
UNIT_MODELS = {
    "Swordsman": "swordsman.png",
    "Archer": "archer.png",
    "Mage": "mage.png",
    "Spearman": "spearman.png",
    "Cavalry": "cavalry.png"
}

# --- Credit display function ---
def display_credits(screen, font):
    screen.fill((0, 0, 0))
    credit_file = "credit.txt"
    if os.path.exists(credit_file):
        with open(credit_file, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = ["[Credits file not found.]"]
    bold_font = pygame.font.SysFont(None, 36, bold=True)
    normal_font = font
    rendered_lines = []
    for line in lines:
        parts = []
        while '[' in line and ']' in line:
            pre, rest = line.split('[', 1)
            bold_part, line = rest.split(']', 1)
            parts.append((pre, False))
            parts.append((f"[{bold_part}]", True))
        parts.append((line, False))
        line_surfaces = []
        for text, is_bold in parts:
            if is_bold:
                surf = bold_font.render(text, True, (255, 255, 255))
            else:
                surf = normal_font.render(text, True, (255, 255, 255))
            line_surfaces.append(surf)
        total_width = sum(s.get_width() for s in line_surfaces)
        height = max(s.get_height() for s in line_surfaces)
        line_surface = pygame.Surface((total_width, height), pygame.SRCALPHA)
        x_offset = 0
        for s in line_surfaces:
            line_surface.blit(s, (x_offset, 0))
            x_offset += s.get_width()
        rendered_lines.append(line_surface)
    
    offset = 0
    running = True
    while running:
        screen.fill((0, 0, 0))
        y = 50 - offset
        for surf in rendered_lines:
            screen.blit(surf, (50, y))
            y += surf.get_height() + 10
        prompt = font.render("Use Up/Down arrows to scroll, press any key to return...", True, (200, 200, 200))
        screen.blit(prompt, (50, y + 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    offset = max(0, offset - 20)
                elif event.key == pygame.K_DOWN:
                    offset += 20
                else:
                    running = False
            elif event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        pygame.time.delay(30)

# --- 자동 문명 감지 (ignore folders starting with "__") ---
def get_available_civilizations():
    civ_folder = "Civilizations"
    civ_list = []
    if os.path.isdir(civ_folder):
        for folder in os.listdir(civ_folder):
            if folder.startswith("__"):
                continue
            path = os.path.join(civ_folder, folder)
            if os.path.isdir(path) and not folder.startswith("Base_"):
                try:
                    module_name = f"Civilizations.{folder}.{folder}_gen"
                    gen_module = __import__(module_name, fromlist=["FULL_NAME"])
                    full_name = getattr(gen_module, "FULL_NAME", folder)
                except Exception as e:
                    print(f"Error importing {folder}_gen: {e}")
                    full_name = folder
                civ_list.append((folder, full_name))
    return civ_list

# --- 문명 상세 정보 반환 ---
def get_civ_detail(civ_abbrev):
    try:
        module_name = f"Civilizations.{civ_abbrev}.{civ_abbrev}_gen"
        gen_module = __import__(module_name, fromlist=["FULL_NAME", "PASSIVE_NAME", "PASSIVE_DESC", "UNIQUE_UNIT", "UNIQUE_UNIT_DESC", "UNIQUE_BUILDING", "UNIQUE_BUILDING_DESC"])
        detail = {
            "name": getattr(gen_module, "FULL_NAME", civ_abbrev),
            "passive": f"{getattr(gen_module, 'PASSIVE_NAME', 'None')}: {getattr(gen_module, 'PASSIVE_DESC', 'None')}",
            "unique_unit": f"{getattr(gen_module, 'UNIQUE_UNIT', 'None')}: {getattr(gen_module, 'UNIQUE_UNIT_DESC', 'None')}",
            "unique_building": f"{getattr(gen_module, 'UNIQUE_BUILDING', 'None')}: {getattr(gen_module, 'UNIQUE_BUILDING_DESC', 'None')}",
            "icon": os.path.join("gfx", civ_abbrev + "_circle.png")
        }
        return detail
    except Exception as e:
        print(f"Error loading civ details for {civ_abbrev}: {e}")
        return {
            "name": civ_abbrev,
            "passive": "None",
            "unique_unit": "None",
            "unique_building": "None",
            "icon": os.path.join("gfx", "default_circle.png")
        }

# --- 문명 선택 화면 ---
def civilization_selection_screen(screen, font):
    available_civs = get_available_civilizations()  # list of (folder_abbrev, full_name)
    if not available_civs:
        available_civs = [("GRL", "Greenland")]
    screen_width, screen_height = screen.get_size()
    list_area_rect = pygame.Rect(0, 0, screen_width, 150)
    detail_area_rect = pygame.Rect(0, 150, screen_width, screen_height - 250)
    start_btn_rect = pygame.Rect(screen_width - 200, screen_height - 80, 150, 50)
    credit_btn_rect = pygame.Rect(screen_width - 150, 10, 120, 40)  # 오른쪽 위 크레딧 버튼
    
    selected_index = 0
    scroll_offset = 0
    running = True
    while running:
        screen.fill((50, 50, 50))
        x = 20 - scroll_offset
        for idx, (civ_abbrev, full_name) in enumerate(available_civs):
            icon_path = os.path.join("gfx", civ_abbrev + "_circle.png")
            if os.path.exists(icon_path):
                icon_img = pygame.image.load(icon_path).convert_alpha()
                icon_img = pygame.transform.scale(icon_img, (100, 100))
            else:
                icon_img = pygame.Surface((100, 100))
                icon_img.fill((100, 100, 100))
            icon_rect = icon_img.get_rect(topleft=(x, 25))
            screen.blit(icon_img, icon_rect)
            name_text = font.render(full_name, True, (255, 255, 255))
            screen.blit(name_text, (x, 130))
            if idx == selected_index:
                pygame.draw.rect(screen, (255, 255, 0), icon_rect, 3)
            x += 120
        
        # 중앙 상세 정보
        detail = get_civ_detail(available_civs[selected_index][0])
        y = detail_area_rect.top + 20
        details = [
            f"Name: {detail['name']}",
            f"Passive: {detail['passive']}",
            f"Unique Unit: {detail['unique_unit']}",
            f"Unique Building: {detail['unique_building']}"
        ]
        for line in details:
            line_surf = font.render(line, True, (255, 255, 255))
            screen.blit(line_surf, (50, y))
            y += line_surf.get_height() + 10
        
        pygame.draw.rect(screen, (0, 128, 0), start_btn_rect)
        start_text = font.render("Start Game", True, (255, 255, 255))
        st_rect = start_text.get_rect(center=start_btn_rect.center)
        screen.blit(start_text, st_rect)
        
        pygame.draw.rect(screen, (0, 0, 128), credit_btn_rect)
        credit_text = font.render("Credits", True, (255, 255, 255))
        ct_rect = credit_text.get_rect(center=credit_btn_rect.center)
        screen.blit(credit_text, ct_rect)
        
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_offset = max(0, scroll_offset - 20)
                elif event.button == 5:
                    scroll_offset += 20
                elif credit_btn_rect.collidepoint(event.pos):
                    display_credits(screen, font)
                elif start_btn_rect.collidepoint(event.pos):
                    return available_civs[selected_index][0]
                else:
                    mx, my = event.pos
                    if list_area_rect.collidepoint(mx, my):
                        index = (mx + scroll_offset - 20) // 120
                        if 0 <= index < len(available_civs):
                            selected_index = index
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_index = max(0, selected_index - 1)
                elif event.key == pygame.K_RIGHT:
                    selected_index = min(len(available_civs) - 1, selected_index + 1)
                elif event.key == pygame.K_RETURN:
                    return available_civs[selected_index][0]
        pygame.time.delay(30)

def show_loading_bar(screen, font):
    screen.fill((0, 0, 0))
    sw, sh = screen.get_size()
    bar_rect = pygame.Rect(50, sh // 2, sw - 100, 40)
    for i in range(101):
        pygame.draw.rect(screen, (100, 100, 100), bar_rect)
        fill_width = int((i / 100) * bar_rect.width)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
        pygame.draw.rect(screen, (0, 255, 0), fill_rect)
        percent_text = font.render(f"Loading... {i}%", True, (255, 255, 255))
        pct_rect = percent_text.get_rect(center=bar_rect.center)
        screen.blit(percent_text, pct_rect)
        pygame.display.flip()
        pygame.time.delay(20)
    screen.fill((0, 0, 0))
    pygame.display.flip()

# --- In-game movement display functions ---
def show_movement_range(screen, unit, cam_x, cam_y, map_pos, effective_move, vis_cols, vis_rows):
    overlay = pygame.Surface((MAIN_TILE_SIZE, MAIN_TILE_SIZE), pygame.SRCALPHA)
    overlay.fill((255, 165, 0, 150))  # Orange overlay
    for j in range(vis_rows):
        for i in range(vis_cols):
            world_x = cam_x + i
            world_y = cam_y + j
            if abs(world_x - unit.x) + abs(world_y - unit.y) <= effective_move:
                pos_x = i * MAIN_TILE_SIZE + map_pos[0]
                pos_y = j * MAIN_TILE_SIZE + map_pos[1]
                screen.blit(overlay, (pos_x, pos_y))

def show_hover_border(screen, cam_x, cam_y, map_pos, vis_cols, vis_rows):
    mx, my = pygame.mouse.get_pos()
    tile_x = cam_x + (mx - map_pos[0]) // MAIN_TILE_SIZE
    tile_y = cam_y + (my - map_pos[1]) // MAIN_TILE_SIZE
    hover_rect = pygame.Rect((tile_x - cam_x) * MAIN_TILE_SIZE + map_pos[0],
                             (tile_y - cam_y) * MAIN_TILE_SIZE + map_pos[1],
                             MAIN_TILE_SIZE, MAIN_TILE_SIZE)
    pygame.draw.rect(screen, (0, 0, 255), hover_rect, 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    sw, sh = screen.get_size()
    base_font = pygame.font.SysFont(None, 36)
    
    selected_civ = civilization_selection_screen(screen, base_font)
    if not selected_civ:
        pygame.quit(); sys.exit()
    show_loading_bar(screen, base_font)
    
    if selected_civ == "GRL":
        from Civilizations.GRL.GRL_gen import GreenlandGeneral
        player_civ_obj = GreenlandGeneral(is_human=True)
    else:
        from civ import Civilization
        player_civ_obj = Civilization(selected_civ, is_human=True)
    
    from civ import Civilization
    ai_civ_objs = [Civilization(f"{DEFAULT_AI_NAME} {i}") for i in range(1, 5)]
    civ_objs = [player_civ_obj] + ai_civ_objs
    
    downsample_factor = 10
    CLIMATE_RASTER_FILENAME = "koppen_geiger_0p1.tif"
    CLIMATE_MAPPING = {
        0: None,
        1: "Af (Tropical Rainforest)",
        2: "Am (Tropical Monsoon)",
        3: "Aw (Tropical Savanna)",
        4: "BWh (Hot Desert)",
        5: "BSh (Hot Semi-Arid)",
        6: "BWk (Cold Desert)",
        7: "BSk (Cold Semi-Arid)",
        8: "Cfa (Humid Subtropical)",
        9: "Cfb (Oceanic)",
        10: "Csa (Hot-Summer Mediterranean)",
        11: "Csb (Warm-Summer Mediterranean)",
        12: "Cwa (Monsoon-influenced Humid Subtropical)",
        13: "Dfa (Hot Summer Continental)",
        14: "Dfb (Warm Summer Continental)",
        15: "Dfc (Subarctic)",
        16: "ET (Tundra)",
        17: "EF (Ice Cap)"
    }
    climate_grid, land_mask, full_width, full_height = load_map_data(CLIMATE_RASTER_FILENAME, downsample_factor, CLIMATE_MAPPING)
    
    from play import Game
    game = Game(full_width, full_height, civ_objs, climate_grid, land_mask)
    
    flags = {}
    for civ in game.civs:
        if civ.name != player_civ_obj.name:
            flag_path = os.path.join("gfx", FLAG_MAPPING.get(DEFAULT_AI_NAME, DEFAULT_AI_FLAG))
        else:
            fallback = civ.internal_name if (hasattr(civ, 'internal_name') and isinstance(civ.internal_name, str)) else str(civ.name)
            flag_path = os.path.join("gfx", FLAG_MAPPING.get(civ.name, fallback + "_circle.png"))
        if os.path.exists(flag_path):
            flags[civ.name] = pygame.image.load(flag_path).convert_alpha()
    
    castle_img = None
    if os.path.exists("castle.png"):
        castle_img = pygame.image.load("castle.png").convert_alpha()
    else:
        print("castle.png not found; capitals will be shown as gray rectangles.")
    
    clock = pygame.time.Clock()
    turn_btn_rect = pygame.Rect(sw - 160, sh - 80, 150, 50)
    mini_surface = create_minimap_surface(game, 1.0)
    mini_x = sw - mini_surface.get_width() - 10
    mini_y = 10
    global selected_unit
    selected_unit = None
    debug_mode = False

    def mask_to_circle(surface):
        size = surface.get_size()
        mask_surface = pygame.Surface(size, pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))
        pygame.draw.circle(mask_surface, (255, 255, 255, 255), (size[0] // 2, size[1] // 2), min(size) // 2)
        result = surface.copy()
        result.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return result

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    debug_mode = not debug_mode
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                elif event.key == pygame.K_n:
                    print("New unit creation is only allowed through barracks training.")
                elif event.key == pygame.K_t:
                    if selected_unit is None:
                        mx, my = pygame.mouse.get_pos()
                        tile_i = mx // MAIN_TILE_SIZE
                        tile_j = my // MAIN_TILE_SIZE
                        cam_x, cam_y, vis_cols, vis_rows = game.draw_main_view(screen, MAIN_TILE_SIZE, castle_img, debug_mode)
                        world_x = cam_x + tile_i
                        world_y = cam_y + tile_j
                        game.train_unit_from_barracks(world_x, world_y, game.civs[0])
                    else:
                        print("Please deselect unit before training from barracks.")
                elif event.key == pygame.K_b:
                    if selected_unit is not None:
                        choice = building_menu(screen, pygame.font.SysFont(None, 30))
                        if choice is not None:
                            sx, sy = selected_unit.x, selected_unit.y
                            game.build_building(choice, sx, sy, game.civs[0])
                    else:
                        print("No unit selected for building construction.")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if turn_btn_rect.collidepoint(mx, my):
                    for unit in [u for u in game.civs[0].units if u.move_order is not None]:
                        sx, sy = unit.x, unit.y
                        dest = unit.move_order
                        dest_tile = game.map[dest[1]][dest[0]]
                        if dest_tile is not None and any(e for e in dest_tile.units if e.civ != unit.civ):
                            defender = [e for e in dest_tile.units if e.civ != unit.civ][0]
                            orig = (sx, sy)
                            game.combat(unit, defender)
                            if defender.hp > 0:
                                if unit in game.map[unit.y][unit.x].units:
                                    game.map[unit.y][unit.x].units.remove(unit)
                                unit.x, unit.y = orig
                                game.map[orig[1]][orig[0]].units.append(unit)
                                unit.move_order = None
                                continue
                        else:
                            if dest[0] != sx:
                                step = 1 if dest[0] > sx else -1
                                for x in range(sx, dest[0] + step, step):
                                    tile = game.map[sy][x]
                                    if tile is not None and tile.owner is None:
                                        tile.owner = unit.civ
                                        unit.civ.territory.add((x, sy))
                            if dest[1] != sy:
                                step = 1 if dest[1] > sy else -1
                                for y in range(sy, dest[1] + step, step):
                                    tile = game.map[y][dest[0]]
                                    if tile is not None and tile.owner is None:
                                        tile.owner = unit.civ
                                        unit.civ.territory.add((dest[0], y))
                        game.map[unit.y][unit.x].units.remove(unit)
                        unit.x, unit.y = dest
                        game.map[unit.y][unit.x].units.append(unit)
                        cost = abs(dest[0] - sx) + abs(dest[1] - sy)
                        unit.remaining_move = max(0, unit.remaining_move - cost)
                        unit.move_order = None
                    game.ai_turn()
                    for unit in game.civs[0].units:
                        unit.remaining_move = unit.base_move * MOVE_MULTIPLIER
                    selected_unit = None
                elif 0 <= mx < sw and 0 <= my < sh - INFO_PANEL_HEIGHT:
                    tile_i = mx // MAIN_TILE_SIZE
                    tile_j = my // MAIN_TILE_SIZE
                    vis_cols = sw // MAIN_TILE_SIZE
                    vis_rows = (sh - INFO_PANEL_HEIGHT) // MAIN_TILE_SIZE
                    map_surface = pygame.Surface((vis_cols * MAIN_TILE_SIZE, vis_rows * MAIN_TILE_SIZE), pygame.SRCALPHA)
                    cam_x, cam_y, vis_cols, vis_rows = game.draw_main_view(map_surface, MAIN_TILE_SIZE, castle_img, debug_mode)
                    masked_map = mask_to_circle(map_surface)
                    map_pos = ((sw - masked_map.get_width()) // 2,
                               (sh - INFO_PANEL_HEIGHT - masked_map.get_height()) // 2)
                    screen.blit(masked_map, map_pos)
                    # Draw overlays (movement range, hover, destination) on top of the map:
                    if selected_unit is not None:
                        effective_move = game.get_effective_move(selected_unit)
                        show_movement_range(screen, selected_unit, cam_x, cam_y, map_pos, effective_move, vis_cols, vis_rows)
                    show_hover_border(screen, cam_x, cam_y, map_pos, vis_cols, vis_rows)
                    if selected_unit is not None and selected_unit.move_order is not None:
                        dest = selected_unit.move_order
                        dx = dest[0] - cam_x
                        dy = dest[1] - cam_y
                        dest_rect = pygame.Rect(dx * MAIN_TILE_SIZE + map_pos[0],
                                                dy * MAIN_TILE_SIZE + map_pos[1],
                                                MAIN_TILE_SIZE, MAIN_TILE_SIZE)
                        pygame.draw.rect(screen, (128, 0, 128), dest_rect, 3)
                    world_x = cam_x + (mx - map_pos[0]) // MAIN_TILE_SIZE
                    world_y = cam_y + (my - map_pos[1]) // MAIN_TILE_SIZE
                    if 0 <= world_x < game.full_width and 0 <= world_y < game.full_height:
                        clicked_tile = game.map[world_y][world_x]
                        if clicked_tile is not None:
                            for unit in clicked_tile.units:
                                if unit.civ.is_human:
                                    selected_unit = unit
                                    break
                        if selected_unit is not None and clicked_tile is not None:
                            game.move_selected_unit(selected_unit, world_x, world_y)
        # Main drawing order: map, units, then overlays and UI.
        vis_cols = sw // MAIN_TILE_SIZE
        vis_rows = (sh - INFO_PANEL_HEIGHT) // MAIN_TILE_SIZE
        player_pop = game.civs[0].population / 1000
        map_surface = pygame.Surface((vis_cols * MAIN_TILE_SIZE, vis_rows * MAIN_TILE_SIZE), pygame.SRCALPHA)
        cam_x, cam_y, vis_cols, vis_rows = game.draw_main_view(map_surface, MAIN_TILE_SIZE, castle_img, debug_mode)
        masked_map = mask_to_circle(map_surface)
        map_pos = ((sw - masked_map.get_width()) // 2,
                   (sh - INFO_PANEL_HEIGHT - masked_map.get_height()) // 2)
        screen.blit(masked_map, map_pos)
        for civ in game.civs:
            if not civ.alive:
                continue
            for unit in civ.units:
                pos = ((unit.x - cam_x) * MAIN_TILE_SIZE + map_pos[0],
                       (unit.y - cam_y) * MAIN_TILE_SIZE + map_pos[1])
                unit_img_path = os.path.join("gfx", UNIT_MODELS.get(unit.unit_type, "default_unit.png"))
                if os.path.exists(unit_img_path):
                    unit_img = pygame.image.load(unit_img_path).convert_alpha()
                    scaled_img = pygame.transform.scale(unit_img, (MAIN_TILE_SIZE, MAIN_TILE_SIZE))
                    scaled_img = mask_to_circle(scaled_img)
                    screen.blit(scaled_img, pos)
                else:
                    fallback = civ.internal_name if (hasattr(civ, 'internal_name') and isinstance(civ.internal_name, str)) else str(civ.name)
                    flag_path = os.path.join("gfx", FLAG_MAPPING.get(civ.name, fallback + "_circle.png"))
                    if os.path.exists(flag_path):
                        flag_img = pygame.image.load(flag_path).convert_alpha()
                        scaled_flag = pygame.transform.scale(flag_img, (MAIN_TILE_SIZE, MAIN_TILE_SIZE))
                        scaled_flag = mask_to_circle(scaled_flag)
                        screen.blit(scaled_flag, pos)
                    else:
                        col = PLAYER_UNIT_COLOR if civ.is_human else AI_UNIT_COLOR
                        center = (pos[0] + MAIN_TILE_SIZE//2, pos[1] + MAIN_TILE_SIZE//2)
                        pygame.draw.circle(screen, col, center, MAIN_TILE_SIZE//3)
        if selected_unit is not None:
            sel_x = (selected_unit.x - cam_x) * MAIN_TILE_SIZE + map_pos[0]
            sel_y = (selected_unit.y - cam_y) * MAIN_TILE_SIZE + map_pos[1]
            pygame.draw.rect(screen, (255, 255, 0), (sel_x, sel_y, MAIN_TILE_SIZE, MAIN_TILE_SIZE), 2)
        # Overlays again (to ensure they're on top)
        if selected_unit is not None:
            effective_move = game.get_effective_move(selected_unit)
            show_movement_range(screen, selected_unit, cam_x, cam_y, map_pos, effective_move, vis_cols, vis_rows)
        show_hover_border(screen, cam_x, cam_y, map_pos, vis_cols, vis_rows)
        if selected_unit is not None and selected_unit.move_order is not None:
            dest = selected_unit.move_order
            dx = dest[0] - cam_x
            dy = dest[1] - cam_y
            dest_rect = pygame.Rect(dx * MAIN_TILE_SIZE + map_pos[0],
                                    dy * MAIN_TILE_SIZE + map_pos[1],
                                    MAIN_TILE_SIZE, MAIN_TILE_SIZE)
            pygame.draw.rect(screen, (128, 0, 128), dest_rect, 3)
        draw_minimap(game, screen, mini_surface, mini_x, mini_y, cam_x, cam_y, vis_cols, vis_rows, flags)
        # UI: Turn button (drawn last)
        pygame.draw.rect(screen, (200, 200, 200), turn_btn_rect)
        btn_text = pygame.font.SysFont(None, 24).render("End Turn", True, (0, 0, 0))
        btn_rect = btn_text.get_rect(center=turn_btn_rect.center)
        screen.blit(btn_text, btn_rect)
        pop_text = f"Population: {player_pop:.1f}K"
        info_text = f"Turn: {game.turn}  Season: {game.season}  {pop_text}  Debug: {'ON' if debug_mode else 'OFF'}"
        pygame.draw.rect(screen, (30, 30, 30), (0, sh - INFO_PANEL_HEIGHT, sw, INFO_PANEL_HEIGHT))
        info_surf = pygame.font.SysFont(None, 24).render(info_text, True, (255, 255, 255))
        screen.blit(info_surf, (10, sh - INFO_PANEL_HEIGHT + 10))
        pygame.display.flip()
        pygame.time.delay(100)
        pygame.time.Clock().tick(10)

if __name__ == "__main__":
    main()
