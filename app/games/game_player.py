from trueskill import Rating

from app.readers.utils.card import NFC_CARD, Card
from app.settings import SLACK_SYNC_INTERVAL
from app.utils.time import utc_now


class GamePlayer:
    def __init__(
            self,
            card,
            slack_user_id=None,
            slack_username=None,
            slack_first_name=None,
            slack_avatar_url=None,
            slack_last_sync=None,
            trueskill_rating=Rating(),
            elo_rating=1200,
            total_games=0,
            games_lost=0,
            games_won=0,
            seconds_played=0
    ):
        self.card = card
        self.slack_user_id = slack_user_id
        self.slack_first_name = slack_first_name
        self.slack_username = slack_username
        self.slack_avatar_url = slack_avatar_url
        self.slack_last_sync = slack_last_sync
        self.trueskill_rating = trueskill_rating
        self.elo_rating = elo_rating
        self.total_games = total_games
        self.games_lost = games_lost
        self.games_won = games_won
        self.seconds_played = seconds_played

    def __repr__(self):
        if self.has_slack_information():
            return '<GamePlayer ' \
                   f'has_slack_information={self.has_slack_information()} ' \
                   f'card={self.card} ' \
                   f'slack_user_id={self.slack_user_id} ' \
                   f'slack_first_name={self.slack_first_name} ' \
                   f'slack_username={self.slack_username} ' \
                   f'slack_avatar_url={self.slack_avatar_url} ' \
                   f'trueskill_rating={self.trueskill_rating} ' \
                   f'elo_rating={self.elo_rating} ' \
                   f'total_games={self.total_games} ' \
                   f'games_won={self.games_won} ' \
                   f'games_lost={self.games_lost}' \
                   '>'
        else:
            return '<GamePlayer ' \
                   f'has_slack_information={self.has_slack_information()} ' \
                   f'card={self.card}>'

    def has_slack_information(self):
        return self.slack_username is not None

    def get_card(self):
        return self.card

    def get_slack_user_id(self):
        return self.slack_user_id

    def set_slack_user_id(self, slack_user_id):
        self.slack_user_id = slack_user_id

    def get_slack_first_name(self):
        return self.slack_first_name

    def set_slack_first_name(self, slack_first_name):
        self.slack_first_name = slack_first_name

    def get_slack_username(self):
        return self.slack_username

    def set_slack_username(self, slack_username):
        self.slack_username = slack_username

    def get_slack_avatar_url(self):
        return self.slack_avatar_url

    def set_slack_avatar_url(self, slack_avatar_url):
        self.slack_avatar_url = slack_avatar_url

    def get_slack_last_sync(self):
        return self.slack_last_sync

    def set_slack_last_sync(self, last_sync):
        self.slack_last_sync = last_sync

    def update_slack_last_sync(self):
        self.set_slack_last_sync(utc_now())

    def should_sync_slack_information(self):
        return (utc_now() - self.get_slack_last_sync()).total_seconds() > SLACK_SYNC_INTERVAL

    def get_trueskill_rating(self):
        return self.trueskill_rating

    def set_trueskill_rating(self, trueskill_rating):
        self.trueskill_rating = trueskill_rating

    def get_elo_rating(self):
        return self.elo_rating

    def set_elo_rating(self, elo_rating):
        self.elo_rating = elo_rating

    def increase_elo_rating(self, amount):
        self.elo_rating += amount

    def decraese_elo_rating(self, amount):
        self.elo_rating -= amount

    def get_total_games(self):
        return self.total_games

    def set_total_games(self, total_games):
        self.total_games = total_games

    def increase_total_games(self):
        self.total_games += 1

    def get_games_won(self):
        return self.games_won

    def set_games_won(self, games_won):
        self.games_won = games_won

    def increase_games_won(self):
        self.games_won += 1

    def get_games_lost(self):
        return self.games_lost

    def set_games_lost(self, games_lost):
        self.games_lost = games_lost

    def increase_games_lost(self):
        self.games_lost += 1

    def get_seconds_played(self):
        return self.seconds_played

    def set_seconds_played(self, seconds_played):
        self.seconds_played = seconds_played

    def add_seconds_played(self, seconds):
        self.seconds_played += seconds

    def to_simplified_object(self):
        if self.has_slack_information():
            return {
                'card_uid': self.card.get_uid(),
                'slack_username': self.slack_username,
                'slack_first_name': self.slack_first_name,
                'slack_avatar_url': self.slack_avatar_url,
                'trueskill_rating': {
                    'mu': self.trueskill_rating.mu,
                    'sigma': self.trueskill_rating.sigma,
                },
                'elo_rating': self.elo_rating,
                'total_games': self.total_games,
                'games_won': self.games_won,
                'games_lost': self.games_lost
            }
        else:
            return {
                'card_uid': self.card.get_uid()
            }

    @staticmethod
    def from_simplified_object(simplified_player):
        return GamePlayer(
            card=Card(
                uid=simplified_player['card_uid'],
                card_type=NFC_CARD  # TODO: set it from Firebase
            ),
            slack_username=simplified_player['slack_username'],
            slack_first_name=simplified_player['slack_first_name'],
            slack_avatar_url=simplified_player['slack_avatar_url'],
            trueskill_rating=Rating(simplified_player['trueskill_rating']),
            elo_rating=simplified_player['rating'] if 'rating' in
                                                      simplified_player else simplified_player['elo_rating'],
            total_games=simplified_player['total_games'],
            games_won=simplified_player['games_won'],
            games_lost=simplified_player['games_lost']
        )

    def to_slack_string(self):
        if self.has_slack_information():
            # Slack has changed how they display mentions:
            # https://api.slack.com/changelog/2017-09-the-one-about-usernames
            return f'<@{self.get_slack_user_id()}>'
        else:
            return f'Ukjent [{self.card.get_uid()}]'
