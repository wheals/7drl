from enum import Enum, auto


class TurnProgress(Enum):
    Finished = auto()
    Ongoing = auto()


class TurnState:
    def __init__(self):
        self.current_turn = 1
        self.progress = TurnProgress.Finished

    def next_turn(self):
        self.current_turn += 1
        self.progress = TurnProgress.Finished
