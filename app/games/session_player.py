from trueskill import Rating

from app.games.game_player import GamePlayer


class SessionPlayer(GamePlayer):
    def __init__(self, card, slack_user_id=None, slack_username=None, slack_first_name=None, slack_avatar_url=None,
                 trueskill_rating=Rating(), elo_rating=1200, total_games=0, games_lost=0, games_won=0):
        super().__init__(card, slack_user_id, slack_username, slack_first_name, slack_avatar_url, trueskill_rating,
                         elo_rating, total_games, games_lost, games_won)

        self.join_time = None
        self.team_key = None

    def get_join_time(self):
        return self.join_time

    def set_join_time(self, join_time):
        self.join_time = join_time

    def reset_join_time(self):
        self.join_time = None

    def get_team_key(self):
        return self.team_key

    def set_team_key(self, team_key):
        self.team_key = team_key

    def has_team_key(self):
        return self.team_key

    def reset_team_key(self):
        self.team_key = None
