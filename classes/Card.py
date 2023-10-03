from enum import Enum
from typing import List


class Category(Enum):
    CONTAGION = 'contagion'
    ACTION = 'action'
    DEFENSE = 'defense'
    OBSTACLE = 'obstacle'


class Card:
    def __init__(self, name, category, quantity):
        self.name: str = name
        self.category: Category = category
        self.amount_in_deck: int = quantity
        self.amount_discarded: int = 0
        self.visible: bool = False

        self.players_with_card: List[int] = []
