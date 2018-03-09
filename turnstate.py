class Turnstate:
    def __init__(self):
        self.current_turn = 0

    def next_turn(self):
        self.current_turn += 1