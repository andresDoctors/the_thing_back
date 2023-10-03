from pathlib import Path


class User:
    def __init__(self, user_id: int, nickname: str):
        self.id: int = user_id
        self.nickname: str = nickname
        self.is_creator: bool = False
        self.icon: Path = Path()

        self.game_id: int = 0
        self.player_id: int = 0
