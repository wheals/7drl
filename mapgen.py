from random import randint, randrange, shuffle


from actor import Actor
from item import Item


def place_player(game_map):
    occupied_spots = [actor.pos for actor in game_map.actors]
    valid_spots = [pos for pos in game_map.terrain if game_map.is_passable(pos) and pos not in occupied_spots]
    player = Actor('player', valid_spots[randrange(0, len(valid_spots))])
    player.is_active_player = True
    game_map.actors.append(player)
    return player


MIN_ROOM_SIZE = 4
MAX_ROOM_SIZE = 10

MIN_CORRIDOR_LENGTH = 0
MAX_CORRIDOR_LENGTH = 5

MAX_ITEMS_PER_LEVEL = 50


def create_h_tunnel(terrain, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        terrain[x, y] = 'floor'


def create_v_tunnel(terrain, x, y1, y2):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        terrain[x, y] = 'floor'


class Room:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def carve_out(self, terrain):
        for x in range(self.x1+1, self.x2):
            for y in range(self.y1+1, self.y2):
                terrain[x, y] = 'floor'

    def inside(self, pos):
        x, y = pos
        return x in range(self.x1, self.x2) and y in range(self.y1, self.y2)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def connect_to(self, other, terrain):
        origin_x = randrange(self.x1+1, self.x2)
        origin_y = randrange(self.y1+1, self.y2)
        dest_x = randrange(other.x1+1, other.x2)
        dest_y = randrange(other.y1+1, other.y2)
        if randint(0, 1) == 1:
            # first move horizontally, then vertically
            create_h_tunnel(terrain, origin_x, dest_x, origin_y)
            create_v_tunnel(terrain, dest_x, origin_y, dest_y)
        else:
            # first move vertically, then horizontally
            create_v_tunnel(terrain, origin_x, origin_y, dest_y)
            create_h_tunnel(terrain, origin_x, dest_x, dest_y)


def generate_map(game_map):
    rooms = []
    col = 0
    while True:
        rooms.append([])
        row = 0
        prev_y = 0
        while True:
            # Get the farthest left this room can start
            if col == 0:
                prev_x = 1
            else:
                prev_x = game_map.width
                for room in rooms[col - 1]:
                    prev_x = min(prev_x, room.x2)
            if prev_y + MIN_CORRIDOR_LENGTH + MIN_ROOM_SIZE >= game_map.height:
                # if we're already at the bottom, we're screwed, go on to next column
                break
            x = prev_x + randint(MIN_CORRIDOR_LENGTH, MAX_CORRIDOR_LENGTH)
            y = prev_y + randint(MIN_CORRIDOR_LENGTH, MAX_CORRIDOR_LENGTH)
            new_x = x + randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            new_y = y + randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
            while True:
                room = Room(x, y, new_x, new_y)
                for old_room in rooms[col - 1]:
                    if room.intersect(old_room):
                        x += 1
                        new_x += 1
                        break
                else:
                    break
            if game_map.height - new_y < MIN_ROOM_SIZE:
                if game_map.height - new_y - MAX_CORRIDOR_LENGTH < MIN_ROOM_SIZE:
                    break
                # try again if we can't fit a room here
                continue
            else:
                new_y = min(new_y, game_map.height - 1)
            prev_y = new_y
            if game_map.width - new_x < MIN_ROOM_SIZE:
                # push down if we can't fit a room here
                continue
            else:
                new_x = min(new_x, game_map.width - 1)
            room = Room(x, y, new_x, new_y)
            room.carve_out(game_map.terrain)
            rooms[col].append(room)
            row += 1
        if prev_x + MIN_CORRIDOR_LENGTH + MIN_ROOM_SIZE >= game_map.width:
            # if we're already at the right, we're screwed, end making rooms
            break
        col += 1
    for i in range(len(rooms)):
        for j in range(len(rooms[i])):
            if i + 1 < len(rooms) and j < len(rooms[i + 1]):
                rooms[i][j].connect_to(rooms[i + 1][j], game_map.terrain)
            if j + 1 < len(rooms[i]):
                rooms[i][j].connect_to(rooms[i][j + 1], game_map.terrain)

    rooms = [room for col in rooms for room in col]
    place_monsters(game_map, rooms)
    place_items(game_map, rooms)


def place_monsters(game_map, rooms):
    shuffle(rooms)
    for i in range(randint(len(rooms) // 2, len(rooms))):
        occupied_spots = [actor.pos for actor in game_map.actors]
        valid_spots = [(x, y) for x in range(rooms[i].x1 + 1, rooms[i].x2) for y in range(rooms[i].y1 + 1, rooms[i].y2)
                       if (x, y) not in occupied_spots]
        game_map.actors.append(Actor('human', valid_spots[randrange(0, len(valid_spots))]))


def total_items(rooms):
    return min(len(rooms), randrange(MAX_ITEMS_PER_LEVEL))


def place_items(game_map, rooms):
    shuffle(rooms)
    for i in range(0, total_items(rooms)):
        valid_spots = [(x, y) for x in range(rooms[i].x1 + 1, rooms[i].x2) for y in range(rooms[i].y1 + 1, rooms[i].y2)]
        game_map.items.append(Item('potion', valid_spots[randrange(0, len(valid_spots))]))
