from app.readers.utils.card import NFC_CARD, Card


class GamePlayer:
    def __init__(
            self,
            card,
            slack_user_id=None,
            slack_username=None,
            slack_first_name=None,
            slack_avatar_url=None,
            rating=1200,
            total_games=0,
            games_lost=0,
            games_won=0
    ):
        self.card = card
        self.slack_user_id = slack_user_id
        self.slack_first_name = slack_first_name
        self.slack_username = slack_username
        self.slack_avatar_url = slack_avatar_url
        self.rating = rating
        self.total_games = total_games
        self.games_lost = games_lost
        self.games_won = games_won

    def __repr__(self):
        if self.has_slack_information():
            return '<GamePlayer ' \
                   f'has_slack_information={self.has_slack_information()} ' \
                   f'card={self.card} ' \
                   f'slack_user_id={self.slack_user_id} ' \
                   f'slack_first_name={self.slack_first_name} ' \
                   f'slack_username={self.slack_username} ' \
                   f'slack_avatar_url={self.slack_avatar_url} ' \
                   f'rating={self.rating} ' \
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

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        self.rating = rating

    def increase_rating(self, amount):
        self.rating += amount

    def decraese_rating(self, amount):
        self.rating -= amount

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

    def to_simplified_object(self):
        if self.has_slack_information():
            return {
                'card_uid': self.card.get_uid(),
                'slack_username': self.slack_username,
                'slack_first_name': self.slack_first_name,
                'slack_avatar_url': self.slack_avatar_url,
                'rating': self.rating,
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
            rating=simplified_player['rating'],
            total_games=simplified_player['total_games'],
            games_won=simplified_player['games_won'],
            games_lost=simplified_player['games_lost']
        )

    def to_slack_string(self):
        if self.has_slack_information():
            # First name only displays on mobile device in Slack for some reason
            return f'<@{self.slack_username}|{self.slack_first_name}>'
        else:
            return f'Ukjent [{self.card.get_uid()}]'
