class ReaderListener:
    def handle_card_read(self, physical_path, card):
        raise NotImplementedError

    def handle_data(self, physical_path, message):
        raise NotImplementedError
