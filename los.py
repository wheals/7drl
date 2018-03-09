import libtcodpy as tcod


def init_los(game_map):
    los_map = tcod.map_new(game_map.width, game_map.height)

    for x in range(game_map.width):
        for y in range(game_map.height):
            tcod.map_set_properties(los_map, x, y, not game_map.is_opaque((x, y)), game_map.is_passable((x, y)))

    return los_map


LOS_RADIUS = 8
LOS_ALGORITHM = 0
LIGHT_WALLS = True


def compute_los(los_map, pos):
    tcod.map_compute_fov(los_map, pos[0], pos[1], LOS_RADIUS, LIGHT_WALLS, LOS_ALGORITHM)

