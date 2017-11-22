from threading import Thread


class GameThreadTimer(Thread):
    def __init__(self, event, game):
        Thread.__init__(self)
        self.stopped = event
        self.game = game

    def run(self):
        while not self.stopped.wait(10.0):
            if self.game.get_current_session().should_reset():
                # Reset the current session if needed
                self.game.get_db().child('current_session').remove()
