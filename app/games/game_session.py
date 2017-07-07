import logging
from datetime import datetime

from app.settings import GAME_PLAYER_REGISTRATION_TIMEOUT

logger = logging.getLogger(__name__)


class GameSession:
    def __init__(self, min_max_card_count):
        self.players = []
        self.join_times = {}
        self.start_time = None
        self.min_max_card_count = min_max_card_count

    def __repr__(self):
        return '<GameSession ' \
               f'has_started={self.start_time is not None} ' \
               f'start_time={self.start_time} ' \
               f'players={self.players}>'

    def set_start_time(self, start_time):
        self.start_time = start_time

    def add_player(self, player):
        self.players.append(player)
        self.join_times[player.get_slack_user_id()] = datetime.now()

    def remove_player(self, player):
        self.players.remove(player)
        self.join_times.pop(player.get_slack_user_id(), None)

    def remove_player_by_card(self, card):
        for player in self.players:
            if card.get_uid() == player.get_card().get_uid():
                self.remove_player(player)

    def get_player(self, i):
        return self.players[i]

    def get_player_by_card(self, card):
        for player in self.players:
            if card.get_uid() == player.get_card().get_uid():
                return player

    def get_players(self):
        return self.players

    def get_players_simplified(self):
        simplified_players = {}
        for player in self.players:
            simplified_players[player.get_card().get_uid()] = {
                **player.to_simplified_object(),
                **{
                    'join_time': self.get_player_join_time(player).isoformat()
                }
            }
        return simplified_players

    def get_player_join_time(self, player):
        return self.join_times[player.player.get_slack_user_id()]

    def has_all_needed_players(self):
        return len(self.players) == self.min_max_card_count

    def get_seconds_elapsed(self):
        return (datetime.now() - self.start_time).total_seconds()

    def is_session_card(self, card):
        for player in self.players:
            if card.get_uid() == player.get_card().get_uid():
                return True
        return False

    def is_session_player(self, player):
        for session_player in self.players:
            if player.get_slack_user_id() == session_player.get_slack_user_id():
                return True
        return False

    def should_reset(self):
        if len(self.players) == 0 or self.has_all_needed_players():
            return False
        for player in self.players:
            if (datetime.now() - self.get_player_join_time(player)).total_seconds() > GAME_PLAYER_REGISTRATION_TIMEOUT:
                return True
        return False

    def start(self):
        # TODO: beep 3 times with buzzer
        self.start_time = datetime.now()
