from copy import copy


import libtcodpy as tcod

from display_char import DisplayChar
from los import init_los


MAX_MAP_WIDTH = 100
MAX_MAP_HEIGHT = 40


def distance(pos1, pos2):
    return max(abs(pos1[0] - pos2[0]), abs(pos1[1] - pos2[1]))


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.actors = []
        self.items = []
        self.terrain = {(x, y): 'wall' for y in range(self.height) for x in range(self.width)}
        self.los_changed = True
        self.los_map = None

    def is_passable(self, pos):
        return self.terrain[pos] == 'floor'

    def is_opaque(self, pos):
        return not self.is_passable(pos)

    def init_los(self):
        self.los_map = init_los(self)

    def actor_at(self, pos):
        return next((actor for actor in self.actors if actor.pos == pos), None)

    def item_at(self, pos):
        return next((item for item in self.items if item.pos == pos), None)


class MapKnowledge(Map):
    def __init__(self, game_map):
        self.width = game_map.width
        self.height = game_map.height
        self.actors = []
        self.items = []
        self.terrain = dict()

    def display_char(self, pos, los_map):
        if pos not in self.terrain:
            return DisplayChar(' ', tcod.black)
        visible = tcod.map_is_in_fov(los_map, pos[0], pos[1])
        actor = self.actor_at(pos)
        if actor:
            return actor.display_char()
        item = self.item_at(pos)
        if item:
            return item.display_char()
        if self.terrain[pos] == 'floor':
            return DisplayChar('.', tcod.white if visible else tcod.dark_grey)
        elif self.terrain[pos] == 'wall':
            return DisplayChar('#', tcod.light_yellow if visible else tcod.dark_yellow)
        else:
            return DisplayChar(' ', tcod.black)

    def update(self, game_map):
        for x in range(game_map.width):
            for y in range(game_map.height):
                if tcod.map_is_in_fov(game_map.los_map, x, y):
                    pos = (x, y)
                    self.terrain[pos] = game_map.terrain[pos]
                    actor = copy(game_map.actor_at(pos))
                    # Remove the actor if we saw it elsewhere earlier
                    if actor:
                        self.actors = [act for act in self.actors if act.id != actor.id]
                        self.actors.append(actor)
                    # Remove the ghost of the actor if we see that it's gone
                    else:
                        self.actors = [act for act in self.actors if act.pos != pos]
                    item = copy(game_map.item_at(pos))
                    if item:
                        # items don't move around on their own, so no need to remove them manually
                        self.items.append(item)
                    else:
                        # but it might have been picked up since it was last seen
                        self.items = [item for item in self.items if item.pos != pos]
