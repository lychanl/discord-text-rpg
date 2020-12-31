from dtrpg.core.game_object import GameObject


class Config(GameObject):
    def __init__(self):
        super().__init__()
        self.player_factory = None
