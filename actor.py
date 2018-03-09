import libtcodpy as tcod


import ai
from display_char import DisplayChar
from command import ActionType, MOVES
from render import show_popup


next_actor_id = 0


def starting_stats(actor_type):
    if actor_type == 'player':
        return 10, 0, 1
    else:
        return 1, 0, 1


class Actor:
    """
    A class to represent both the player and monsters
    """
    def __init__(self, type, pos):
        global next_actor_id
        self.kind = type
        self.pos = pos
        if type == 'player':
            self.ai = ai.PlayerAI(self)
        else:
            self.ai = ai.SimpleMonsterAI(self)
        self.is_active_player = False
        self.max_hp, self.defense, self.power = starting_stats(type)
        self.hp = self.max_hp
        self.alive = True
        self.id = next_actor_id
        next_actor_id += 1
        self.inventory = []

    def name(self):
        if self.kind == 'player':
            if self.is_active_player:
                return 'you'
            else:
                return 'your past self'
        else:
            return 'the ' + self.kind

    def possessive(self):
        if self.kind == 'player':
            if self.is_active_player:
                return "your"
            else:
                return "your past self's"
        else:
            return "the " + self.kind + "'s"

    def conjugate(self, verb):
        if self.is_active_player:
            return verb
        else:
            return verb + 's'

    def execute(self, command, game_map):
        action = command.action
        if action in MOVES:
            x, y = self.pos
            dx, dy = MOVES[action]
            newpos = x + dx, y + dy
            other = game_map.actor_at(newpos)
            if other:
                return self.attack(other)
            else:
                return self.move_to(game_map, newpos)
        if action is ActionType.Rest:
            return [{'time': 100}]
        if action is ActionType.Exit:
            return [{'exit': True}]
        if action is ActionType.Pickup:
            return self.pickup(game_map)
        if action is ActionType.Describe:
            if self.is_active_player:
                show_popup(command.item.description(), 'DESCRIBE')
            return [{'time': 0}]
        if action is ActionType.Apply:
            used, results = command.item.apply(self)
            if used:
                self.inventory.remove(command.item)
            return results
        return [{'time': 0}]

    def pickup(self, game_map):
        if len(self.inventory) >= 26:
            return [{'time': 0}, {'message': 'Inventory full.'}]
        item = game_map.item_at(self.pos)
        if not item:
            return [{'time': 0}]
        self.inventory.append(item)
        game_map.items.remove(item)
        return [{'message': '{} {} up {}.'.format(self.name().capitalize(),
                                                  self.conjugate('pick'),
                                                  item.name())},
                {'time': 100}]

    def attack(self, target):
        results = []
        damage = self.power - target.defense

        results.append({'message': '{} {} {}.'.format(self.name().capitalize(),
                                                      self.conjugate('hit'),
                                                      target.name())})
        if damage > 0:
            results.extend(target.hurt(damage))
        results.append({'time': 100})
        return results

    def hurt(self, amount):
        results = []
        self.hp -= amount
        if self.hp <= 0:
            results.append({'dead': self})
        return results

    def die(self):
        self.alive = False
        return '{} {}!'.format(self.name().capitalize(), self.conjugate('die'))

    def move_to(self, map, pos):
        if not map.is_passable(pos):
            return [{'time': 0}]
        if map.actor_at(pos):
            return [{'time': 0}]
        x, y = self.pos
        self.pos = pos
        if self.is_active_player:
            map.los_changed = True
        return [{'time': 100}]

    def display_char(self):
        if self.kind == 'player':
            return DisplayChar('@', tcod.white)
        elif self.kind == 'human':
            return DisplayChar('h', tcod.light_cyan)
        else:
            return DisplayChar('?', tcod.magenta)
