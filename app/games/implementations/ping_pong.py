from app.games.office_game import OfficeGame


class PingPongGame(OfficeGame):
    def __init__(self):
        super().__init__(
            game_name='Ping Pong',
            game_version='0.2.0'
        )

    def read_card(self, team_key, card):
        if super(PingPongGame, self).read_card(team_key, card):
            if len(self.get_current_session().get_players()) == 2:
                # We have all the players/cards needed to start the game. Start the actual session
                self.start_session()
        return True
