from datetime import datetime

import serial

from app.readers.rfid.cards.em4200 import ID_TYPE as ID_TYPE_EM4200
from app.readers.rfid.cards.em4200 import EM4200Card
from app.readers.serial.serial_reader import SerialReader


class RFIDReader(SerialReader):
    def reader(self):
        try:
            while self.connected and self._reader_alive:
                if not self._should_read():
                    continue
                # read all that is there or wait for one byte
                self.reader_buffer_string += self.serial_instance\
                    .read(self.serial_instance.in_waiting or 1)\
                    .decode('UTF-8')
                if '\r\n' in self.reader_buffer_string:
                    lines = self.reader_buffer_string.split('\r\n')
                    self.reader_last_received = lines[-2]
                    self.reader_buffer_string = lines[-1]
                    self.reader_last_read_time = datetime.now()
                    if self.reader_last_received[:1] == ID_TYPE_EM4200:
                        for reader_listener in self.reader_listeners:
                            reader_listener.handle_card_read(EM4200Card(self.reader_last_received[1:]))
                    else:
                        for reader_listener in self.reader_listeners:
                            reader_listener.handle_data(self.reader_last_received)
        except serial.SerialException:
            self.connected = False
            # TODO: Handle exception (reconnect?) instead of re-raise
            raise
