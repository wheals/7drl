import libtcodpy as tcod


from display_char import DisplayChar


next_item_id = 0


class Item:
    def __init__(self, kind, pos):
        global next_item_id
        self.kind = kind
        self.pos = pos
        self.id = next_item_id
        next_item_id += 1

    def name(self):
        return 'the ' + self.kind

    def description(self):
        if self.kind == 'potion':
            return 'A magical potion. Use it to restore your HP.'
        else:
            return 'A buggy item!'

    def display_char(self):
        if self.kind == 'potion':
            return DisplayChar('!', tcod.blue)
        else:
            return DisplayChar('?', tcod.white)

    def apply(self, actor):
        if self.kind == 'potion':
            if actor.hp == actor.max_hp:
                return False, [{'message': 'You are already at full HP.', 'player_only': 'true'}]
            else:
                actor.hp = min(actor.hp + 5, actor.max_hp)
                return True, [{'message': '{} HP is restored.'.format(actor.possessive().capitalize())}]
        return False, []
