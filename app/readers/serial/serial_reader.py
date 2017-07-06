import threading
from datetime import datetime

import serial
from serial.tools import list_ports

from app.readers.exceptions import ReaderCouldNotConnect, ReaderNotFound
from app.readers.port import Port


class SerialReader:
    @staticmethod
    def find_reader(vendor_id, product_id, serial_number):
        vendor_id, product_id = vendor_id.replace('0x', ''), product_id.replace('0x', '')
        port = SerialReader._find_reader(vendor_id, product_id, serial_number)
        return Port(
            port.device,
            hex(port.vid),
            hex(port.pid),
            port.serial_number
        )

    @staticmethod
    def _find_reader(vendor_id, product_id, serial_number):
        vendor_id, product_id = vendor_id.replace('0x', ''), product_id.replace('0x', '')
        try:
            ports = list_ports.grep(f'{vendor_id}:{product_id}')
            for port in ports:
                if port.serial_number == serial_number:
                    return port
        except StopIteration:
            raise ReaderNotFound(vendor_id, product_id, serial_number)
        else:
            raise ReaderNotFound(vendor_id, product_id, serial_number)

    @staticmethod
    def get_ports():
        ports = []
        for n, port in enumerate(sorted(list_ports.comports()), 1):
            ports.append(Port(
                port.device,
                hex(port.vid),
                hex(port.pid),
                port.serial_number
            ))
        return ports

    # TODO: add partiy, rtscts, xonxoff
    def __init__(self, serial_port, baudrate=9600, read_delay=1):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.read_delay = read_delay
        self.connected = False
        self._reader_alive = None
        self.receiver_thread = None
        self.reader_listeners = []
        self.reader_buffer_string = ''
        self.reader_last_received = None
        self.reader_last_read_time = datetime.now()

        try:
            self.serial_instance = serial.serial_for_url(
                self.serial_port.path,
                self.baudrate,
                do_not_open=True
            )

            if not hasattr(self.serial_instance, 'cancel_read'):
                # enable timeout for alive flag polling if cancel_read is not available
                self.serial_instance.timeout = 1
        except serial.SerialException as exception:
            raise ReaderCouldNotConnect(
                self.serial_port,
                exception
            )

    def add_read_listener(self, listener):
        self.reader_listeners.append(listener)

    def connect(self):
        """Connect to the reader and start the worker threads"""
        self.serial_instance.open()
        self.connected = True
        self._start_reader()

        while self.connected:
            pass

    def _start_reader(self):
        """Start reader thread"""
        self._reader_alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader, name='rx')
        self.receiver_thread.daemon = True
        self.receiver_thread.start()

    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        self._reader_alive = False
        if hasattr(self.serial_instance, 'cancel_read'):
            self.serial_instance.cancel_read()
        self.receiver_thread.join()

    def reader(self):
        raise NotImplementedError

    def _should_read(self):
        return (datetime.now() - self.reader_last_read_time).total_seconds() > self.read_delay
