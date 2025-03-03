# map_.py
import pygame
import rasterio
import numpy as np

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

def load_map_data(filename, downsample_factor, climate_mapping):
    with rasterio.open(filename) as raster:
        full_width = raster.width // downsample_factor
        full_height = raster.height // downsample_factor
        climate_array = raster.read(1, out_shape=(full_height, full_width))
    land_mask = [[(int(climate_array[y, x]) != 0) for x in range(full_width)] for y in range(full_height)]
    climate_grid = [[None for _ in range(full_width)] for _ in range(full_height)]
    for y in range(full_height):
        for x in range(full_width):
            if land_mask[y][x]:
                value = int(climate_array[y, x])
                climate = climate_mapping.get(value)
                if climate is None:
                    lat = 90 - (y / full_height) * 180
                    if lat >= 66.5 or lat <= -66.5:
                        climate = "EF (Ice Cap)"
                    elif -23.5 <= lat <= 23.5:
                        climate = "Af (Tropical Rainforest)"
                    elif 23.5 < lat < 45:
                        climate = "Dfb (Warm Summer Continental)"
                    else:
                        climate = "Humid Subtropical"
                climate_grid[y][x] = climate
            else:
                climate_grid[y][x] = None
    return climate_grid, land_mask, full_width, full_height

def create_minimap_surface(game, scale):
    mini_w = int(game.full_width * scale)
    mini_h = int(game.full_height * scale)
    mini_array = np.zeros((game.full_height, game.full_width, 3), dtype=np.uint8)
    for y in range(game.full_height):
        for x in range(game.full_width):
            if game.land_mask[y][x]:
                climate = game.climate_grid[y][x]
                color = TILE_COLORS.get(climate, (200, 200, 200))
                mini_array[y, x] = color
            else:
                mini_array[y, x] = WATER_COLOR
    full_mini = pygame.surfarray.make_surface(np.transpose(mini_array, (1, 0, 2)))
    mini_surface = pygame.transform.scale(full_mini, (mini_w, mini_h))
    return mini_surface
