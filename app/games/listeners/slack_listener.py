import logging

from app.games.game_listener import GameListener
from app.settings import SLACK_CHANNEL, SLACK_DEV_CHANNEL, SLACK_USERNAME

logger = logging.getLogger(__name__)


class SlackListener(GameListener):
    def __init__(self, game):
        super().__init__(game)

    def _format_end_session_player_string(self, player_name, trueskill_rating, trueskill_delta, elo_rating=None, elo_delta=None):
        player_string = f'{player_name}\nNy Trueskill rating: {trueskill_rating} [{trueskill_delta}]'
        if elo_rating is not None:
               player_string += f'\nNy ELO rating: {elo_rating} [{elo_delta}]'
        return player_string

    def _send_message_to_slack(self, message, channel=SLACK_CHANNEL, attachments=None):
        if attachments is not None:
            result = self.game.slack.chat.post_message(
                channel=channel,
                username=SLACK_USERNAME,
                attachments=attachments
            )
        else:
            result = self.game.slack.chat.post_message(
                channel=channel,
                username=SLACK_USERNAME,
                text=message
            )
        if result.successful:
            logger.info(f'Slack message sent to #{channel}: {message}')
        else:
            logger.error(f'Failed sending message to slack: {result}')

    def on_startup(self):
        self._send_message_to_slack(
            message=f'OfficeGames Client v{self.game.get_core_version()} has started, running "{self.game.get_name()}" '
                    f'v{self.game.get_version()} game',
            channel=SLACK_DEV_CHANNEL
        )

    def on_pending_card_registration_timeout(self, pending_registration, card):
        self._send_message_to_slack(
            message=f'Tiden for å registrere kortet: {card.get_uid()} har løpt ut, du må starte registreringen på nytt',
            channel=pending_registration['user_id']
        )

    def on_new_card_registration(self, player, card):
        self._send_message_to_slack(
            message=f'Et nytt kort har blitt registrert til din bruker: {card.get_uid()}',
            channel=player.get_slack_user_id()
        )

        self._send_message_to_slack(message=f'{player.to_slack_string()} has registrert et nytt kort: {card.get_uid()}')

    def on_unregistered_card_read(self, card):
        self._send_message_to_slack(message=f'Ukjent kort prøvde å spille: {card.get_uid()}')

    def on_register_player(self, player):
        message = f'*{self.game.game_name}* - Spiller registrerte seg for å spille'
        self._send_message_to_slack(
            message=message,
            attachments=[{
                'fallback': message,
                'pretext': message,
                'mrkdwn_in': ['text', 'pretext', 'fields'],
                'color': '#439FE0',
                'fields': [
                    {
                        'title': f'Spiller #{ len(self.game.current_session.get_players()) }',
                        'value': f'{player.to_slack_string()}\n'
                                 f'ELO Rating: {player.get_elo_rating()}\n'
                                 f'Trueskill Rating: {player.get_trueskill_rating().mu}',
                        'short': False
                    }
                ]
            }],
        )

    def on_already_in_session(self, player, card):
        self._send_message_to_slack(
            message=f'Kortet {card.get_uid()} eller et av dine andre kort er allerede registrert i den nåværende økten',
            channel=player.get_slack_user_id()
        )

    def on_existing_active_session(self, player, card):
        self._send_message_to_slack(
            message=f'En økt eksisterer allerede, vennligst vent {self.game.get_seconds_left()} sekunder',
            channel=player.get_slack_user_id()
        )

    def on_start_session(self, teams, is_1vs1=False):
        message = f'*{self.game.game_name}* - Spill startet'
        fields = []
        i = 1
        for team in teams:
            title = f'Team {team.get_team_key().upper()}'
            value = ''

            for slack_user_id, player in team.get_players():
                if is_1vs1:
                    title = f'Spiller #{i}'
                    value += f'{player.to_slack_string()}\n' \
                             f'ELO Rating: {player.get_elo_rating()}\n' \
                             f'Trueskill Rating: {player.get_trueskill_rating()}'
                else:
                    if value != '':
                        value += '\n'
                    value += f'Spiller #{i}\n' \
                             f'{player.to_slack_string()}\n' \
                             f'ELO Rating: {player.get_elo_rating()}\n' \
                             f'Trueskill Rating: {player.get_trueskill_rating()}'
                i += 1

            if not is_1vs1:
                i = 1

            fields.append({
                'title': title,
                'value': value,
                'short': True
            })

        self._send_message_to_slack(
            message=message,
            attachments=[{
                'fallback': message,
                'pretext': message,
                'mrkdwn_in': ['text', 'pretext', 'fields'],
                'color': 'warning',
                'fields': fields
            }]
        )

    def on_end_session(self, winner_team, loser_team, rated_trueskill_rating_groups, new_elo_ratings=None, is_1vs1=False):
        message = f'*{self.game.game_name}* - Spill ferdig'
        if is_1vs1:
            winner_player = winner_team.get_first_player()
            winner_new_elo_rating = new_elo_ratings[winner_player.get_slack_user_id()]
            winner_new_trueskill_rating = rated_trueskill_rating_groups[0][winner_player.get_slack_user_id()]
            loser_player = loser_team.get_first_player()
            loser_new_elo_rating = new_elo_ratings[loser_player.get_slack_user_id()]
            loser_new_trueskill_rating = rated_trueskill_rating_groups[1][loser_player.get_slack_user_id()]
            self._send_message_to_slack(
                message=message,
                attachments=[{
                    'fallback': message,
                    'pretext': message,
                    'mrkdwn_in': ['text', 'pretext', 'fields'],
                    'color': 'good',
                    'fields': [
                        {
                            'title': 'Vinner',
                            'value': self._format_end_session_player_string(
                                player_name=winner_player.to_slack_string(),
                                trueskill_rating=winner_new_trueskill_rating.mu,
                                trueskill_delta=f'+{winner_new_trueskill_rating.mu - winner_player.get_trueskill_rating().mu}',
                                elo_rating=winner_new_elo_rating,
                                elo_delta=f'+{winner_new_elo_rating - winner_player.get_elo_rating()}'
                            ),
                            'short': True
                        },
                        {
                            'title': 'Taper',
                            'value': self._format_end_session_player_string(
                                player_name=loser_player.to_slack_string(),
                                trueskill_rating=loser_new_trueskill_rating.mu,
                                trueskill_delta=f'-{loser_player.get_trueskill_rating().mu - loser_new_trueskill_rating.mu}',
                                elo_rating=loser_new_elo_rating,
                                elo_delta=f'-{loser_player.get_elo_rating() - loser_new_elo_rating}'
                            ),
                            'short': True
                        }
                    ]
                }],
            )
        else:
            fields = []
            for team in [winner_team, loser_team]:
                is_winner = team.get_team_key() == winner_team.get_team_key()

                value = f'Poeng: {team.get_points()}\n'

                for slack_user_id, player in team.get_players().items():
                    if is_winner:
                        player_string = self._format_end_session_player_string(
                            player_name=player.to_slack_string(),
                            trueskill_rating=rated_trueskill_rating_groups[0][slack_user_id].mu,
                            trueskill_delta=f'+{rated_trueskill_rating_groups[0][slack_user_id].mu - player.get_trueskill_rating().mu}'
                        )
                    else:
                        player_string = self._format_end_session_player_string(
                            player_name=player.to_slack_string(),
                            trueskill_rating=rated_trueskill_rating_groups[1][slack_user_id].mu,
                            trueskill_delta=f'-{player.get_trueskill_rating().mu - rated_trueskill_rating_groups[1][slack_user_id].mu}'
                        )
                    value += f'\n{player_string}'

                fields.append({
                    'title': f'{"Vinner" if is_1vs1 else "Taper"} - Team {team.get_team_key().upper()}',
                    'value': value,
                    'short': True
                })

    def on_session_timeout(self, session):
        self._send_message_to_slack(message=f'Tiden på økten har løp ut, starter en ny økt!')
