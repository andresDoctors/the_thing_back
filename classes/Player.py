from enum import Enum
from typing import List


class Rol(Enum):
    THE_THING = 'theThing'
    INFECTED = 'infected'
    HUMAN = 'human'


class CurrentPhase(Enum):
    INACTIVE = 'inactive'
    ACTIVE = 'active'
    DEFENDING = 'defending'


class Player:
    def __init__(self, player_id, user_id):
        self.id: int = player_id
        self.rol: Rol = Rol.HUMAN
        self.alive: bool = True
        self.quarantine: bool = False
        self.current_phase: CurrentPhase = CurrentPhase.INACTIVE

        self.user: int = user_id
        self.left_player: int = 0
        self.right_player: int = 0
        self.hand: List[str] = []
