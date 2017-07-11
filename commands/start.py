import logging

from app.games.implementations.ping_pong import PingPongGame
from app.settings import READER_VENDOR_ID, READER_PRODUCT_ID, READER_A_PHYSICAL_PATH, READER_B_PHYSICAL_PATH
from app.readers.hid.hid_reader import HIDReader
from app.readers.reader_listener import ReaderListener


def start(game_slug):
    logging.basicConfig(level=logging.DEBUG)

    game = PingPongGame()

    class CapraNFCReader(ReaderListener):
        def handle_card_read(self, physical_path, card):
            game.register_card(physical_path, card)

        def handle_data(self, physical_path,message):
            pass

    ports = HIDReader.find_readers(
        READER_VENDOR_ID,
        READER_PRODUCT_ID,
        [READER_A_PHYSICAL_PATH, READER_B_PHYSICAL_PATH]
    )
    reader = HIDReader(ports)
    reader.add_read_listener(CapraNFCReader())
    reader.connect()
