import logging
import threading

import sys

import time

from app.constants import TEAM_A, TEAM_B
from app.games.implementations.ping_pong import PingPongGame
from app.sensors import MPR121
from app.settings import READER_VENDOR_ID, READER_PRODUCT_ID, READER_A_PHYSICAL_PATH, READER_B_PHYSICAL_PATH, \
    SENSOR_A_ADD_POINT_PIN, SENSOR_A_REMOVE_POINT_PIN, SENSOR_B_ADD_POINT_PIN, SENSOR_B_REMOVE_POINT_PIN
from app.readers.hid.hid_reader import HIDReader
from app.readers.reader_listener import ReaderListener

logging.basicConfig(level=logging.INFO)
game = PingPongGame()


class CapraNFCReader(ReaderListener):
    def handle_card_read(self, physical_path, card):
        game.read_card(
            team_key=TEAM_A if physical_path == READER_A_PHYSICAL_PATH else TEAM_B,
            card=card
        )

    def handle_data(self, physical_path, message):
        pass


def start_reader():
    print('Starting reader thread')
    ports = HIDReader.find_readers(
        vendor_id=READER_VENDOR_ID,
        product_id=READER_PRODUCT_ID,
        physical_paths=[READER_A_PHYSICAL_PATH, READER_B_PHYSICAL_PATH]
    )
    reader = HIDReader(ports)
    reader.add_read_listener(CapraNFCReader())
    reader.connect()


def start_sensor_input():
    print('Starting sensor thread')
    gpio_pins = [
        SENSOR_A_ADD_POINT_PIN,
        SENSOR_A_REMOVE_POINT_PIN,
        SENSOR_B_ADD_POINT_PIN,
        SENSOR_B_REMOVE_POINT_PIN
    ]

    cap = MPR121.MPR121()

    if not cap.begin():
        print('Error initializing MPR121.  Check your wiring!')
        sys.exit(1)

    last_touched = cap.touched()
    while True:
        current_touched = cap.touched()
        # Check each pin's last and current state to see if it was pressed or released.
        for gpio_pin in gpio_pins:
            # Each pin is represented by a bit in the touched value.  A value of 1
            # means the pin is being touched, and 0 means it is not being touched.
            pin_bit = 1 << gpio_pin
            # First check if transitioned from not touched to touched.
            if current_touched & pin_bit and not last_touched & pin_bit:
                if gpio_pin == SENSOR_A_ADD_POINT_PIN:
                    game.add_point(TEAM_A)
                elif gpio_pin == SENSOR_A_ADD_POINT_PIN:
                    game.remove_point(TEAM_A)
                elif gpio_pin == SENSOR_B_ADD_POINT_PIN:
                    game.add_point(TEAM_B)
                elif gpio_pin == SENSOR_B_ADD_POINT_PIN:
                    game.remove_point(TEAM_B)
        # Update last state and wait a short period before repeating.
        last_touched = current_touched
        time.sleep(0.1)


def start(game_slug):
    reader_thread = threading.Thread(target=start_reader)
    reader_thread.start()
    sensor_thread = threading.Thread(target=start_sensor_input)
    sensor_thread.start()
