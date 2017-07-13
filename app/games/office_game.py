import logging
from datetime import datetime

import pytz
from slacker import Slacker
from slugify import slugify
from trueskill import Rating, quality, rate

from app.constants import TEAM_A, TEAM_B
from app.games.exceptions import CardExists, UnregisteredCardException
from app.games.game_player import GamePlayer
from app.games.game_session import GameSession
from app.games.listeners.console_listener import ConsoleListener
from app.games.listeners.slack_listener import SlackListener
from app.games.session_player import SessionPlayer
from app.settings import GAME_CARD_REGISTRATION_TIMEOUT, GAME_SESSION_TIME, SLACK_MESSAGES_ENABLED, SLACK_TOKEN
from app.utils.elo_rating import calculate_new_rating
from app.utils.firebase import get_firebase
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class OfficeGame:
    def __init__(self, game_name, game_version):
        self.core_version = '0.2.1'
        self.game_name = game_name
        self.game_version = game_version
        self.game_slug = slugify(game_name)
        self.game_listeners = []
        self.firebase = get_firebase()
        self.current_session = GameSession()
        self.slack = Slacker(SLACK_TOKEN)
        self.add_game_listener(ConsoleListener(self))
        if SLACK_MESSAGES_ENABLED:
            self.add_game_listener(SlackListener(self))

        # TODO: get remote session
        # remote_current_session = self.get_current_remote_session()
        # if remote_current_session is not None:
            # TODO: isoformat -> datetime for session_started?
        #    self.get_current_session().set_start_time(remote_current_session['session_started'])
        #    for simplified_player in remote_current_session['players']:
        #        self.get_current_session().add_player(GamePlayer.from_simplified_object(simplified_player))

        if SLACK_MESSAGES_ENABLED:
            # Send a notification to listeners
            for game_listener in self.game_listeners:
                game_listener.on_startup()

    def _get_db(self):
        return self.firebase.database().child('games').child(self.game_slug)

    def _check_pending_card_registration(self, card):
        pending_registration = self.firebase.database()\
            .child('pending_registrations')\
            .child(card.get_uid()) \
            .get().val()

        if pending_registration is None:
            return False

        registration_datetime = datetime.fromtimestamp(
            int(pending_registration['timestamp'] / 1000)
        ).replace(tzinfo=pytz.utc)

        if (utc_now() - registration_datetime).total_seconds() > GAME_CARD_REGISTRATION_TIMEOUT:
            # Send a notification to listeners
            for game_listener in self.game_listeners:
                game_listener.on_pending_card_registration_timeout(pending_registration=pending_registration, card=card)
            return False

        self.register_new_game_card(card, pending_registration['user_id'])
        self.firebase.database() \
            .child('pending_registrations') \
            .child(card.get_uid()) \
            .remove()
        return True

    def _get_remote_player_information(self, card):
        existing_card = self.firebase.database().child('cards').child(card.get_uid()).get().val()

        if existing_card is None or 'slack_user_id' not in existing_card:
            raise UnregisteredCardException(card)

        # Initialize the SessionPlayer object
        game_player = SessionPlayer(card=card)

        # The card exists and registered to a player, grab the player from the database
        existing_player = self.firebase.database()\
            .child('players')\
            .child(existing_card['slack_user_id'])\
            .get().val()

        # The player exists in the database, add the relevant information to the SessionPlayer object
        game_player.set_slack_user_id(existing_card['slack_user_id'])
        game_player.set_slack_username(existing_player['slack_username'])
        game_player.set_slack_first_name(existing_player['slack_first_name'])
        game_player.set_slack_avatar_url(existing_player['slack_avatar_url'])

        # Check if the player has statistics in the current game_slug
        existing_player_statistics = self._get_db() \
            .child('player_statistics') \
            .child(existing_card['slack_user_id']) \
            .get().val()

        if existing_player_statistics is not None:
            # The player has statistics stored in the database, add it to the GamePlayer object
            if 'elo_rating' in existing_player_statistics:
                game_player.set_elo_rating(existing_player_statistics['elo_rating'])

            game_player.set_trueskill_rating(Rating(
                mu=existing_player_statistics['trueskill_rating']['mu'],
                sigma=existing_player_statistics['trueskill_rating']['sigma']
            ))
            game_player.set_total_games(existing_player_statistics['total_games'])
            game_player.set_games_won(existing_player_statistics['games_lost'])
            game_player.set_games_lost(existing_player_statistics['games_won'])

        return game_player

    def get_core_version(self):
        return self.core_version

    def get_version(self):
        return self.game_version

    def get_name(self):
        return self.game_name

    def get_slug(self):
        return self.game_slug

    def add_game_listener(self, listener):
        self.game_listeners.append(listener)

    def get_current_session(self):
        return self.current_session

    # Used for administration
    def register_new_game_card(self, card, slack_user_id):
        existing_card = self.firebase.database().child('cards').child(card.get_uid()).get().val()

        if existing_card is None:
            # Card does not exist, insert the card
            self.firebase.database().child('cards').child(card.get_uid()).set({
                'slack_user_id': slack_user_id,
                'registration_date': utc_now().isoformat()
            })
        else:
            # Card exists in the database
            if 'slack_user_id' not in existing_card:
                # Card exists, but is not registered to a player, update the owner (player)
                self.firebase.database().child('cards').child(card.get_uid()).update({
                    'slack_user_id': slack_user_id
                })
            elif existing_card['slack_user_id'] == slack_user_id:
                # The card is already registered to this Slack user, ignore
                logger.debug(f'Card {card} is already registered under user ID {slack_user_id}, doing nothing')
                return
            else:
                # The card exists under another player
                raise CardExists(card, existing_card['slack_user_id'])

        # Does the player exists in the database?
        existing_player = self.firebase.database().child('players').child(slack_user_id).get().val()

        if existing_player is not None:
            # Player exists in the database, just append the card to the player
            self.firebase.database()\
                .child('players')\
                .child(slack_user_id)\
                .child('cards')\
                .child(card.get_uid())\
                .set(True)

            player = GamePlayer(
                card=card,
                slack_user_id=slack_user_id,
                slack_username=existing_player['slack_username'],
                slack_first_name=existing_player['slack_first_name'],
                slack_avatar_url=existing_player['slack_avatar_url']
            )
        else:
            # Player does not exist, get the slack information of the user
            slack_user_response = self.slack.users.info(slack_user_id)
            if slack_user_response is None or not slack_user_response.successful:
                logger.error(slack_user_response.error)
                return
            slack_profile = slack_user_response.body['user']['profile']
            new_player = {
                'slack_username': slack_user_response.body['user']['name'],
                'slack_first_name': slack_profile['first_name'],
                'slack_avatar_url': slack_profile['image_512'] if 'image_512' in slack_profile else None,
                'registration_date': utc_now().isoformat(),
                'cards': {
                    card.get_uid(): True
                }
            }

            player = GamePlayer(
                card=card,
                slack_user_id=slack_user_id,
                slack_username=new_player['slack_username'],
                slack_first_name=new_player['slack_first_name'],
                slack_avatar_url=new_player['slack_avatar_url']
            )

            # Add the new player to the database, with the card added in the card list
            self.firebase.database().child('players').child(slack_user_id).set(new_player)

            # Add the player to the player statistics of the current game_slug
            self._get_db().child('player_statistics').child(slack_user_id).set({
                'trueskill_rating': {
                    'mu': Rating().mu,
                    'sigma': Rating().sigma,
                },
                'elo_rating': 1200,
                'total_games': 0,
                'games_won': 0,
                'games_lost': 0
            })

        # Send a notification to listeners
        for game_listener in self.game_listeners:
            game_listener.on_new_card_registration(player=player, card=card)

    def start_session(self):
        self.get_current_session().start()

        session_teams = self.get_current_session().get_teams()

        # Set the start time of the current session in remote
        self._get_db().child('current_session').update({
            'session_started': self.get_current_session().start_time.isoformat(),
            'trueskill_quality': quality(self.get_current_session().get_rating_groups())
        })

        # Send a notification to listeners
        for game_listener in self.game_listeners:
            game_listener.on_start_session(teams=session_teams, is_1vs1=self.get_current_session().is_1vs1())

    def end_session(self, winner_team_key):
        loser_team_key = TEAM_A if winner_team_key == TEAM_A else TEAM_B

        all_players = self.get_current_session().get_all_players()

        # Remove the winner from the player list and return the first player (loser for now)
        winner_team = self.get_current_session().get_team(winner_team_key)
        loser_team = self.get_current_session().get_team(loser_team_key)

        new_elo_ratings = {}

        if self.get_current_session().is_1vs1():
            # Calculate the players new rating (has to be 1vs1)
            new_elo_ratings[winner_team.get_first_player().get_slack_user_id()] = calculate_new_rating(
                player_rating=winner_team.get_first_player().get_elo_rating(),
                opponent_rating=loser_team.get_first_player().get_elo_rating(),
                player_won=True
            )
            new_elo_ratings[loser_team.get_first_player().get_slack_user_id()] = calculate_new_rating(
                player_rating=loser_team.get_first_player().get_elo_rating(),
                opponent_rating=winner_team.get_first_player().get_elo_rating(),
                player_won=False
            )

        rated_trueskill_rating_groups = rate([
            winner_team.get_rating_group(),
            loser_team.get_rating_group()
        ])

        session_info = {
            'session_started': self.get_current_session().start_time.isoformat(),
            'session_ended': utc_now().isoformat(),
            'versus_string': self.get_current_session().get_versus_string(),
            'trueskill_quality': quality([
                winner_team.get_rating_group(),
                loser_team.get_rating_group()
            ]),
            'winner': {},
            'loser': {}
        }

        for team in self.get_current_session().get_teams():
            is_winner = team.get_team_key() == winner_team_key
            team_index = 'winner' if is_winner else 'loser'
            session_info[team_index] = {
                'points': team.get_points(),
                'players': {}
            }
            for slack_user_id, player in team.get_players().items():
                new_trueskill_rating = rated_trueskill_rating_groups[0 if is_winner else 1][player.get_slack_user_id()]
                session_info[team_index]['players'][player.get_slack_user_id()] = {
                    'trueskill_rating': {
                        'mu': {
                            'before': player.get_trueskill_rating().mu,
                            'after': new_trueskill_rating.mu,
                            'delta': new_trueskill_rating.mu - player.get_trueskill_rating().mu
                        },
                        'sigma': {
                            'before': player.get_trueskill_rating().sigma,
                            'after': new_trueskill_rating.sigma,
                            'delta': new_trueskill_rating.sigma - player.get_trueskill_rating().sigma
                        }
                    }
                }
                if self.get_current_session().is_1vs1():
                    new_elo_rating = new_elo_ratings[player.get_slack_user_id()]
                    session_info[team_index]['players'][player.get_slack_user_id()]['elo_rating'] = {
                        'before': player.get_elo_rating(),
                        'after': new_elo_rating,
                        'delta': new_elo_rating - player.get_elo_rating()
                    }

        # Push the current session (which has ended) to the list of sessions in Firebase
        results = self._get_db().child('sessions').push(session_info)

        # Push the current session id/pk to the list of sessions for each card
        for player in all_players:
            is_winner = player.get_team_key() == winner_team_key
            new_trueskill_rating = rated_trueskill_rating_groups[0 if is_winner else 1][player.get_slack_user_id()]

            existing_player_statistics = self._get_db()\
                .child('player_statistics')\
                .child(player.get_slack_user_id())\
                .get().val()

            # Initialize the information
            player_statistics = {
                'trueskill_rating': {
                    'mu': new_trueskill_rating.mu,
                    'sigma': new_trueskill_rating.sigma
                },
                'total_games': existing_player_statistics['total_games'] + 1,
                'games_won': existing_player_statistics['games_won'] + (1 if is_winner else 0),
                'games_lost': existing_player_statistics['games_lost'] + (1 if not is_winner else 0)
            }

            player_session = {
                'card_uid': player.get_card().get_uid(),
                'winner': is_winner,
                'versus_string': self.get_current_session().get_versus_string(),
                'team_key': player.get_team_key(),
                'trueskill_rating': {
                    'mu': {
                        'new': new_trueskill_rating.mu,
                        'delta': new_trueskill_rating.mu - player.get_trueskill_rating().mu
                    },
                    'sigma': {
                        'new': new_trueskill_rating.sigma,
                        'delta': new_trueskill_rating.sigma - player.get_trueskill_rating().sigma
                    }
                }
            }

            # Only set elo_rating if it's a 1vs1 session
            if self.get_current_session().is_1vs1():
                new_elo_rating = new_elo_ratings[player.get_slack_user_id()]
                player_session['elo_rating'] = {
                    'new': new_elo_rating,
                    'delta': new_elo_rating - player.get_elo_rating()
                }

                player_statistics['elo_rating'] = new_elo_rating

            # Set the player statistics
            self._get_db().child('player_statistics').child(player.get_slack_user_id()).set(player_statistics)

            # Add the session to the players' session list
            self.firebase.database()\
                .child('players')\
                .child(player.get_slack_user_id())\
                .child('sessions')\
                .child(self.game_slug)\
                .child(results['name'])\
                .set(player_session)

        # Send a notification to listeners
        for game_listener in self.game_listeners:
            game_listener.on_end_session(
                winner_team=winner_team,
                loser_team=loser_team,
                rated_trueskill_rating_groups=rated_trueskill_rating_groups,
                new_elo_ratings=new_elo_ratings,
                is_1vs1=self.get_current_session().is_1vs1()
            )

        # Create a new session placeholder (it doesn't start until we call .start())
        self.current_session = GameSession()

        # Reset / remove the remote session
        self._get_db().child('current_session').remove()

    def get_seconds_left(self):
        return GAME_SESSION_TIME - self.get_current_session().get_seconds_elapsed()

    def _update_team_readiness(self, team_key):
        if self.get_current_session().has_all_needed_players() \
                and not self.get_current_session().get_team(team_key).is_ready():
            self.get_current_session().get_team(team_key).set_ready(True)

            # Update the current session in Firebase (that a team is ready)
            self._get_db().child('current_session').update({
                'teams': self.get_current_session().get_teams_simplified()
            })

            # Are all the teams ready?
            if self.get_current_session().are_all_teams_ready():
                self.start_session()

    def add_point(self, team_key):
        if self.get_current_session().has_started():
            # Add 1 point to the team
            self.get_current_session().get_team(team_key).add_point()

            # Update the current session in Firebase (their points)
            self._get_db().child('current_session').update({
                'teams': self.get_current_session().get_teams_simplified()
            })

            return True
        self._update_team_readiness(team_key)
        return False

    def remove_point(self, team_key):
        if self.get_current_session().has_started():
            if self.get_current_session().get_team(team_key).get_points() <= 0:
                return False
            # Remove 1 point from the team
            self.get_current_session().get_team(team_key).remove_point()

            # Update the current session in Firebase (their points)
            self._get_db().child('current_session').update({
                'teams': self.get_current_session().get_teams_simplified()
            })

            return True
        self._update_team_readiness(team_key)
        return False

    def read_card(self, team_key, card):
        if self._check_pending_card_registration(card):
            return False
        try:
            reset_session = False
            player = self._get_remote_player_information(card)
            if self.get_current_session().has_started():
                if self.get_current_session().is_session_card(card):
                    # The player / card already exists in the session
                    # Send a notification to listeners
                    for game_listener in self.game_listeners:
                        game_listener.on_already_in_session(player=player, card=card)
                    return False
                elif self.get_seconds_left() > 0:
                    # A new card tried to register whilst there was an active sessions
                    # Send a notification to listeners
                    for game_listener in self.game_listeners:
                        game_listener.on_existing_active_session(player=player, card=card)
                    return False
                else:
                    # We have a new card, create a new session
                    reset_session = True
            elif self.get_current_session().should_reset():
                reset_session = True
            elif self.get_current_session().is_session_card(card) \
                    or self.get_current_session().is_session_player(player):
                # The player / card already exists in the session
                # Send a notification to listeners
                for game_listener in self.game_listeners:
                    game_listener.on_already_in_session(player=player, card=card)
                return False

            if reset_session:
                # Send a notification to listeners
                for game_listener in self.game_listeners:
                    game_listener.on_session_timeout(session=self.get_current_session())
                self.current_session = GameSession()

            # Add player to the session
            self.get_current_session().add_player(team_key, player)

            # Update the current session in Firebase as well
            self._get_db().child('current_session').update({
                'versus_string': self.get_current_session().get_versus_string(),
                'teams': self.get_current_session().get_teams_simplified()
            })

            # Send a notification to listeners
            for game_listener in self.game_listeners:
                game_listener.on_register_player(player=player)
            return True
        except UnregisteredCardException:
            # Send a notification to listeners
            for game_listener in self.game_listeners:
                game_listener.on_unregistered_card_read(card=card)
            return False

    def get_current_remote_session(self):
        return self._get_db().child('current_session').get().val()

    def has_current_remote_session(self):
        return self.get_current_remote_session() is not None
