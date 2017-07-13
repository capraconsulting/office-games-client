class GameTeam:
    def __init__(self, team_key):
        self.team_key = team_key
        self.players = {}
        self.points = 0
        self.ready = False

    def get_team_key(self):
        return self.team_key

    def get_points(self):
        return self.points

    def add_point(self):
        self.add_points(1)

    def add_points(self, amount):
        self.points += amount

    def remove_point(self):
        self.remove_points(1)

    def remove_points(self, amount):
        self.points -= amount

    def get_players_simplified(self):
        simplified_players = {}
        for slack_user_id, player in self.players:
            simplified_players[slack_user_id] = {
                **player.to_simplified_object(),
                **{
                    'join_time': player.get_join_time().isoformat()
                }
            }

    def get_players(self):
        return self.players

    def get_player(self, slack_user_id):
        return self.players[slack_user_id]

    def get_first_player(self):
        return next(iter(self.players))

    def add_player(self, player):
        player.set_team_key(self.team_key)
        self.players[player.get_slack_user_id()] = player

    def remove_player(self, player):
        player.set_team_key(None)
        self.players.pop(player.get_slack_user_id(), None)

    def is_team_player(self, player):
        return player.get_slack_user_id() in self.players

    def get_rating_group(self):
        rating_group = {}
        for slack_user_id, player in self.players:
            rating_group[slack_user_id] = player.get_trueskill_rating()
        return rating_group

    def is_ready(self):
        return self.is_ready

    def set_ready(self, ready):
        self.ready = ready
