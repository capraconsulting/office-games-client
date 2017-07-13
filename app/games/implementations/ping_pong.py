from app.constants import TEAM_B, TEAM_A
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

    def add_point(self, team_key):
        # The super method returns true if a point was added successfully
        if super(PingPongGame, self).add_point(team_key):
            opponent_key = TEAM_A if team_key == TEAM_B else TEAM_B
            team = self.get_current_session().get_team(team_key)
            opponent = self.get_current_session().get_team(opponent_key)
            total_points = team.get_points() + opponent.get_points()
            points_delta = team.get_points() - opponent.get_points()

            # Check if team has the needed points to win
            if team.get_points() >= 11 and points_delta >= 2:
                # We have a winner! End the session
                self.end_session(team.get_team_key())
            else:
                # We do not have a winner yet.
                # Set the current active team, so that we know who is supposed to serve
                update_active_team = False

                # Current active team
                active_team_key = self.get_current_session().get_active_team_key()

                if active_team_key is None:
                    # Initialize the first active team
                    self.get_current_session().set_active_team_key(team_key)
                    update_active_team = True
                elif (team.get_points() >= 10 and team.get_points() >= 10) \
                        or (total_points % 2 == 0):
                    # Serves should alternate each round between teams when both teams reach 10 points.
                    # Else if the number is even, the serve should alternate (every 2 rounds).
                    opposite_team_key = TEAM_A if active_team_key == TEAM_B else TEAM_B
                    self.get_current_session().set_active_team_key(opposite_team_key)
                    update_active_team = True

                if update_active_team:
                    # Update the remote current session
                    self._get_db().child('current_session').update({
                        'active_team': self.get_current_session().get_active_team_key()
                    })
        return True

    def remove_point(self, team_key):
        # The super method returns true if a point was added successfully
        if super(PingPongGame, self).remove_point(team_key):
            opponent_key = TEAM_A if team_key == TEAM_B else TEAM_B
            team = self.get_current_session().get_team(team_key)
            opponent = self.get_current_session().get_team(opponent_key)
            total_points = team.get_points() + opponent.get_points()

            # Current active team
            active_team_key = self.get_current_session().get_active_team_key()

            if (team.get_points() >= 10 and team.get_points() >= 10) \
                    or (total_points % 2 == 0):
                # Serves should alternate each round between teams when both teams reach 10 points.
                # Else if the number is even, the serve should alternate (every 2 rounds).
                opposite_team_key = TEAM_A if active_team_key == TEAM_B else TEAM_B
                self.get_current_session().set_active_team_key(opposite_team_key)

                # Update the remote current session
                self._get_db().child('current_session').update({
                    'active_team': self.get_current_session().get_active_team_key()
                })
        return True
