from enum import Enum
from typing import List


class StatusType(Enum):
    LOBBY = 'lobby'
    IN_GAME = 'inGame'
    FINISHED = 'finished'


class OrderOfTurns(Enum):
    CLOCKWISE = 'clockwise'
    COUNTERCLOCKWISE = 'counterclockwise'


class Game:
    def __init__(self, game_id, game_name, password, min, max):
        self.id: int = game_id
        self.name: str = game_name
        self.password: str = password
        self.min: int = min
        self.max: int = max

        self.users: List[int] = []
        self.status: StatusType = StatusType.LOBBY
        self.order_of_turns: OrderOfTurns = OrderOfTurns.CLOCKWISE
