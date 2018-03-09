from enum import Enum, auto


import libtcodpy as tcod


class Command:
    def __init__(self, action, item=None):
        self.action = action
        self.item = item # item do do it with, if any


class ActionType(Enum):
    MoveUp = auto()
    MoveDown = auto()
    MoveLeft = auto()
    MoveRight = auto()
    MoveUpLeft = auto()
    MoveUpRight = auto()
    MoveDownLeft = auto()
    MoveDownRight = auto()
    Rest = auto()
    Pickup = auto()
    Describe = auto()
    Apply = auto()
    Exit = auto()

def takes_time(action):
    return action is not ActionType.Quit


command_keys = {
    tcod.KEY_UP: ActionType.MoveUp,
    tcod.KEY_DOWN: ActionType.MoveDown,
    tcod.KEY_LEFT: ActionType.MoveLeft,
    tcod.KEY_RIGHT: ActionType.MoveRight,
    'k': ActionType.MoveUp,
    'j': ActionType.MoveDown,
    'h': ActionType.MoveLeft,
    'l': ActionType.MoveRight,
    'y': ActionType.MoveUpLeft,
    'u': ActionType.MoveUpRight,
    'b': ActionType.MoveDownLeft,
    'n': ActionType.MoveDownRight,
    's': ActionType.Rest,
    ',': ActionType.Pickup,
    'i': ActionType.Describe,
    'a': ActionType.Apply,
    tcod.KEY_ESCAPE: ActionType.Exit,
}


MOVES = {ActionType.MoveUp: (0, -1),
         ActionType.MoveDown: (0, 1),
         ActionType.MoveRight: (1, 0),
         ActionType.MoveLeft: (-1, 0),
         ActionType.MoveUpLeft: (-1, -1),
         ActionType.MoveUpRight: (1, -1),
         ActionType.MoveDownLeft: (-1, 1),
         ActionType.MoveDownRight: (1, 1)}


def handle_key(key):
    return command_keys.get(key.vk) or command_keys.get(chr(key.c))
