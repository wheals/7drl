from random import randrange


import libtcodpy as tcod


from command import handle_key, ActionType, MOVES, Command
from render import show_popup


def find_astar(origin, dest, game_map):
    # Create a FOV map that has the dimensions of the map
    fov = tcod.map_new(game_map.width, game_map.height)

    # Scan the current map each turn and set all the walls as unwalkable
    for y1 in range(game_map.height):
        for x1 in range(game_map.width):
            tcod.map_set_properties(fov, x1, y1, not game_map.is_opaque((x1, y1)),
                                    game_map.is_passable((x1, y1)))

    # Scan all the objects to see if there are objects that must be navigated around
    # Check also that the object isn't self or the target (so that the start and the end points are free)
    # The AI class handles the situation if self is next to the target so it will not use this A* function anyway
    for pos in [actor.pos for actor in game_map.actors]:
        if pos != origin and pos != dest:
            # Set the tile as a wall so it must be navigated around
            tcod.map_set_properties(fov, pos[0], pos[1], True, False)

    # Allocate a A* path
    my_path = tcod.path_new_using_map(fov, 1)

    # Compute the path between self's coordinates and the target's coordinates
    tcod.path_compute(my_path, origin[0], origin[1], dest[0], dest[1])

    # Check if the path exists
    if not tcod.path_is_empty(my_path):
        # Find the next coordinates in the computed full path
        x, y = tcod.path_walk(my_path, True)
        # Delete the path to free memory
        tcod.path_delete(my_path)
        if x or y:
            delta = (x - origin[0], y - origin[1])
            for act, move in MOVES.items():
                if move == delta:
                    return act


class AI:
    def __init__(self, owner):
        self.owner = owner


class SimpleMonsterAI(AI):
    def next_move(self, **kwargs):
        if not self.owner.alive:
            return Command(None)
        target = kwargs.get('target')
        game_map = kwargs.get('game_map')
        pos = self.owner.pos
        if tcod.map_is_in_fov(game_map.los_map, pos[0], pos[1]):
            return Command(find_astar(pos, target.pos, game_map))
        else:
            return Command([ActionType.MoveUp,
                            ActionType.MoveDown,
                            ActionType.MoveLeft,
                            ActionType.MoveRight][randrange(0, 4)])


class PlayerAI(AI):
    def next_move(self, **kwargs):
        action = handle_key(tcod.console_wait_for_keypress(True))
        prompt = None
        if action is ActionType.Describe:
            prompt = 'Describe what?'
        elif action is ActionType.Apply:
            prompt = 'Apply/use what?'
        if prompt:
            key = show_popup(prompt, 'CHOOSE ITEM')
            index = key.c - ord('a')
            if index in range(0, len(self.owner.inventory)):
                return Command(action, self.owner.inventory[index])
            else:
                return Command(None)
        else:
            return Command(action)
