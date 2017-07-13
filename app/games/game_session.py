import logging

from app.constants import TEAM_A, TEAM_B
from app.games.game_team import GameTeam
from app.settings import GAME_PLAYER_REGISTRATION_TIMEOUT
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class GameSession:
    def __init__(self):
        self.teams = {
            TEAM_A: GameTeam(TEAM_A),
            TEAM_B: GameTeam(TEAM_B)
        }
        self.all_players = []
        self.start_time = None
        self.active_team_key = None

    def __repr__(self):
        return '<GameSession ' \
               f'has_started={self.has_started()} ' \
               f'start_time={self.start_time} ' \
               f'teams={self.teams}>'

    def set_start_time(self, start_time):
        self.start_time = start_time

    def add_player(self, team_key, player):
        player.set_join_time(utc_now())
        player.set_team_key(team_key)
        self.teams[team_key].add_player(player)
        self.all_players.append(player)

    def remove_player(self, team_key, player):
        player.reset_join_time()
        player.reset_team_key()
        self.teams[team_key].remove_player(player)
        self.all_players.remove(player)

    def get_all_players(self):
        return self.all_players

    def get_team(self, team_key):
        return self.teams[team_key]

    def get_teams(self):
        return self.teams

    def get_versus_string(self):
        versus_string = ''
        for team in self.teams:
            if versus_string == '':
                versus_string = len(team.get_players())
            else:
                versus_string += f'vs{len(team.get_players())}'
        return versus_string

    def get_rating_groups(self):
        rating_groups = [{}, {}]
        for player in self.all_players:
            team_index = 0 if player.get_team_key() == TEAM_A else 1
            rating_groups[team_index][player.get_slack_user_id()] = player.get_trueskill_rating()
        return rating_groups

    def get_teams_simplified(self):
        simplified_teams = {}
        for team in self.teams:
            simplified_teams[team.get_team_key()] = {
                'ready': team.is_ready(),
                'points': team.get_points(),
                'players': team.get_players_simplified()
            }
        return simplified_teams

    def get_seconds_elapsed(self):
        return (utc_now() - self.start_time).total_seconds()

    def is_session_card(self, card):
        for player in self.all_players:
            if card.get_uid() == player.get_card().get_uid():
                return True
        return False

    def is_session_player(self, player):
        for session_player in self.all_players:
            if player.get_slack_user_id() == session_player.get_slack_user_id():
                return True
        return False

    def has_all_needed_players(self):
        return len(self.teams[TEAM_A].get_players()) >= 1 and len(self.teams[TEAM_B].get_players()) >= 1

    def is_1vs1(self):
        return len(self.teams[TEAM_A].get_players()) == 1 and len(self.teams[TEAM_B].get_players()) == 1

    def should_reset(self):
        return len(self.all_players) == 1 and \
               (utc_now() - self.all_players[0].get_join_time()).total_seconds() > \
               GAME_PLAYER_REGISTRATION_TIMEOUT

    def get_active_team_key(self):
        return self.active_team_key

    def set_active_team_key(self, team_key):
        self.active_team_key = team_key

    def has_started(self):
        return self.start_time is not None

    def start(self):
        # TODO: beep 3 times with buzzer
        self.start_time = utc_now()

    def are_all_teams_ready(self):
        return self.teams[TEAM_A].is_ready() and self.teams[TEAM_B].is_ready()
