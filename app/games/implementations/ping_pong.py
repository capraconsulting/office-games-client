from app.games.office_game import OfficeGame


class PingPongGame(OfficeGame):
    def __init__(self):
        super().__init__(
            game_name='Ping Pong',
            game_version='0.1.0',
            min_max_card_count=2
        )
