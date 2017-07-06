class ReaderListener:
    def handle_card_read(self, card):
        raise NotImplementedError

    def handle_data(self, message):
        raise NotImplementedError
