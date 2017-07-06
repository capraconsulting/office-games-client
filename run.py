#!/usr/bin/python
import logging

from app.games.implementations.ping_pong import PingPongGame
from app.settings import READER_VENDOR_ID, READER_PRODUCT_ID
from app.readers.hid.hid_reader import HIDReader
from app.readers.reader_listener import ReaderListener


logging.basicConfig(level=logging.DEBUG)

game = PingPongGame()


class CapraNFCReader(ReaderListener):
    def handle_card_read(self, card):
        game.register_card(card)

    def handle_data(self, message):
        pass


ports = HIDReader.find_readers(READER_VENDOR_ID, READER_PRODUCT_ID, None)
reader = HIDReader(ports)
reader.add_read_listener(CapraNFCReader())
reader.connect()
