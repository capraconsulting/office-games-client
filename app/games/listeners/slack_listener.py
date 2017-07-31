import logging

import math

from app.games.game_listener import GameListener
from app.settings import SLACK_CHANNEL, SLACK_DEV_CHANNEL, SLACK_USERNAME

logger = logging.getLogger(__name__)


class SlackListener(GameListener):
    def __init__(self, game):
        super().__init__(game)

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
                                 f'Trueskill Level: {player.get_trueskill_rating().mu * 10}',
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

    def on_start_session(self, players):
        message = f'*{self.game.game_name}* - Spill startet'
        fields = []
        for i in range(len(players)):
            fields.append({
                'title': f'Spiller #{i + 1}',
                'value': f'{players[i].to_slack_string()}\n'
                         f'Trueskill Level: {math.floor(players[i].get_trueskill_rating().mu * 10)}',
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

    def on_end_session(self, winner_player, winner_new_elo_rating, winner_new_trueskill_rating,
                       loser_player, loser_new_elo_rating, loser_new_trueskill_rating):
        winner_trueskill_delta = math.floor((winner_player.get_trueskill_rating().mu - winner_new_trueskill_rating.mu) * 10)
        loser_trueskill_delta = math.floor((loser_new_trueskill_rating.mu - loser_player.get_trueskill_rating().mu) * 10)
        message = f'*{self.game.game_name}* - Spill ferdig'
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
                        'value': f'{winner_player.to_slack_string()}\n'
                                 f'Ny Trueskill level: {winner_new_trueskill_rating.mu} '
                                 f'[+{winner_trueskill_delta}]',
                        'short': True
                    },
                    {
                        'title': 'Taper',
                        'value': f'{loser_player.to_slack_string()}\n'
                                 f'Ny Trueskill level: {loser_new_trueskill_rating.mu} '
                                 f'[-{loser_trueskill_delta}]',
                        'short': True
                    }
                ]
            }],
        )

    def on_session_timeout(self, session):
        self._send_message_to_slack(message=f'Tiden på økten har løp ut, starter en ny økt!')
