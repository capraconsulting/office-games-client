class GameListener:
    def __init__(self, game):
        self.game = game

    def get_game(self):
        return self.game

    def on_startup(self):
        pass

    def on_pending_card_registration_timeout(self, pending_registration, card):
        pass

    def on_new_card_registration(self, player, card):
        pass

    def on_unregistered_card_read(self, card):
        pass

    def on_already_in_session(self, player, card):
        pass

    def on_existing_active_session(self, player, card):
        pass

    def on_start_session(self, teams, is_1vs1=False):
        pass

    def on_end_session(self, winner_team, loser_team, rated_trueskill_rating_groups, new_elo_ratings=None, is_1vs1=False):
        pass

    def on_session_timeout(self, session):
        pass

    def on_register_player(self, player):
        pass
