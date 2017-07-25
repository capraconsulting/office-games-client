import logging
import time

from app.games.game_listener import GameListener
from app.settings import SOUND_OUTPUT

logger = logging.getLogger(__name__)


class SoundListener(GameListener):
    def __init__(self, game):
        super().__init__(game)
        self.gpio = SOUND_OUTPUT == 'gpio'
        if self.gpio:
            try:
                import RPi.GPIO as GPIO
            except RuntimeError:
                print("Error importing RPi.GPIO! This is probably because you need superuser privileges. "
                      "You can achieve this by using 'sudo' to run your script")
            GPIO.setmode(GPIO.BOARD)

    def play_sound(self):
        if self.gpio:
            NUM_CYCLES = 10
            start = time.time()
            for impulse_count in range(NUM_CYCLES):
                GPIO.wait_for_edge(25, GPIO.FALLING)
            duration = time.time() - start  # seconds to run for loop
            frequency = NUM_CYCLES / duration  # in Hz
        pass

    def on_startup(self):
        logger.info(f'OfficeGames Client v{self.game.get_core_version()} has started, running "{self.game.get_name()}" '
                    f'v{self.game.get_version()} game')

    def on_pending_card_registration_timeout(self, pending_registration, card):
        logger.info(f'Pending registration {pending_registration} timed out for card {card}')

    def on_new_card_registration(self, player, card):
        logger.info(f'New card {card} has been registered to player {player}')

    def on_unregistered_card_read(self, card):
        logger.info(f'Unknown card {card} tried to register for a "{self.game.get_name()}" game')

    def on_register_player(self, player):
        logger.info(f'{player} has registered for a "{self.game.get_name()}" game')

    def on_already_in_session(self, player, card):
        logger.info(f'Player {player} tried to register card {card} to current session'
                    f'but the card or player is already a part of the session')

    def on_existing_active_session(self, player, card):
        logger.info(f'Player {player} tried to register to an active session. '
                    f'Please wait {self.game.get_seconds_left()} seconds.')

    def on_start_session(self, players):
        logger.info(f'New "{self.game.get_name()}" session started with players: {players}')

    def on_end_session(self, winner_player, winner_new_elo_rating, winner_new_trueskill_rating,
                       loser_player, loser_new_elo_rating, loser_new_trueskill_rating):
        logger.info(f'"{self.game.get_name()}" session ended. '
                    f'Winner: {winner_player} [{winner_new_elo_rating}] [{winner_new_trueskill_rating}]. '
                    f'Loser: {loser_player} [{loser_new_elo_rating}] [{loser_new_trueskill_rating}]')

    def on_session_timeout(self, session):
        logger.info(f'Session time ran out. Starting a new session! Session that ran out: {session}')
