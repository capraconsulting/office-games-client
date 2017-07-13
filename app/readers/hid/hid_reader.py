import selectors
import threading
from datetime import datetime

import evdev
from evdev import InputDevice, categorize, ecodes

from app.readers.exceptions import ReaderNotFound
from app.readers.nfc.cards.mifare_classic import MifareClassicCard
from app.readers.port import Port
from app.utils.time import utc_now

SCAN_CODES = {
    # Scancode: ASCIICode
    0: None, 1: 'ESC', 2: '1', 3: '2', 4: '3', 5: '4', 6: '5', 7: '6', 8: '7', 9: '8',
    10: '9', 11: '0', 12: '-', 13: '=', 14: 'BKSP', 15: 'TAB', 16: 'Q', 17: 'W', 18: 'E', 19: 'R',
    20: 'T', 21: 'Y', 22: '', 23: 'I', 24: 'O', 25: 'P', 26: '[', 27: ']', 28: 'CRLF', 29: 'LCTRL',
    30: 'A', 31: 'S', 32: 'D', 33: 'F', 34: 'G', 35: 'H', 36: 'J', 37: 'K', 38: 'L', 39: ';',
    40: '"', 41: '`', 42: 'LSHFT', 43: '\\', 44: 'Z', 45: 'X', 46: 'C', 47: 'V', 48: 'B', 49: 'N',
    50: 'M', 51: ',', 52: '.', 53: '/', 54: 'RSHFT', 56: 'LALT', 100: 'RALT'
}


class HIDReader:
    @staticmethod
    def find_readers(vendor_id, product_id, physical_paths):
        try:
            vendor_id = int(vendor_id, 16)
            product_id = int(product_id, 16)
            readers = []
            for port in HIDReader.get_ports():
                if port.vendor_id == vendor_id \
                        and port.product_id == product_id \
                        and port.phys in physical_paths:
                    readers.append(port)
            return readers
        except StopIteration:
            raise ReaderNotFound(vendor_id, product_id, None)

    @staticmethod
    def get_ports():
        ports = []
        for device in [evdev.InputDevice(fn) for fn in evdev.list_devices()]:
            ports.append(Port(
                path=device.fn,
                vendor_id=device.info.vendor,
                product_id=device.info.product,
                physical_port=device.phys,
                serial_number=None  # Not supported with evdev
            ))
        return ports

    def __init__(self, hid_ports, read_delay=1):
        self.hid_ports = hid_ports
        self.reader_devices = []
        self.selector = selectors.DefaultSelector()
        self.read_delay = read_delay
        self.connected = False
        self._reader_alive = None
        self.receiver_thread = None
        self.reader_listeners = []
        self.reader_buffer_strings = []
        self.reader_last_received = []
        self.reader_last_read_time = []

        for i in range(len(hid_ports)):
            self.reader_buffer_strings.append('')
            self.reader_last_received.append(None)
            self.reader_last_read_time.append(utc_now())

    def add_read_listener(self, listener):
        self.reader_listeners.append(listener)

    def connect(self):
        """Connect to the reader and start the worker threads"""
        self.connected = True

        for port in self.hid_ports:
            reader_device = InputDevice(port.path)
            reader_device.grab()
            self.reader_devices.append(reader_device)
            self.selector.register(reader_device, selectors.EVENT_READ)

        self._start_reader()

        while self.connected:
            pass

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start hid->console thread
        self.reader()
        # TODO: Enable threading when stable
        # self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        # self.receiver_thread.daemon = True
        # self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        self.receiver_thread.join()

    def reader(self):
        try:
            while self.connected and self._reader_alive:
                for key, mask in self.selector.select():
                    reader_device = key.fileobj
                    reader_index = self.reader_devices.index(reader_device)
                    for event in reader_device.read():
                        if event.type == ecodes.EV_KEY:
                            data = categorize(event)  # Save the event temporarily to introspect it
                            if data.keystate == 1:  # Down events only
                                if data.scancode in SCAN_CODES:
                                    if (data.scancode != 42) and (data.scancode != 28):
                                        self.reader_buffer_strings[reader_index] += SCAN_CODES.get(data.scancode)
                                    if data.scancode == 28:
                                        data_string = self.reader_buffer_strings[reader_index]
                                        # TODO: Add more checks
                                        if len(data_string) == 8:
                                            for listener in self.reader_listeners:
                                                listener.handle_card_read(
                                                    physical_path=reader_device.phys,
                                                    card=MifareClassicCard(data_string)
                                                )
                                        else:
                                            for listener in self.reader_listeners:
                                                listener.handle_card_read(
                                                    physical_path=reader_device.phys,
                                                    card=data_string
                                                )
                                        self.reader_buffer_strings[reader_index] = ''

        except Exception as e:
            self.connected = False
            # TODO: Handle exception (reconnect?) instead of re-raise
            raise

    def _should_read(self, reader_index):
        return (utc_now() - self.reader_last_read_time[reader_index]).total_seconds() > self.read_delay
