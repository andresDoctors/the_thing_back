from enum import Enum


class Side(Enum):
    LEFT = 'left'
    RIGHT = 'right'


class Adjacency:
    def __init__(self, left_player_id, right_player_id):
        self.left_player: int = left_player_id
        self.right_player: int = right_player_id
        self.blocked: bool = False
