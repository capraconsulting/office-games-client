def format_reader_port_message(message, reader_port, error):
    return f'{message} with {reader_port}. Error: {error}'


def format_reader_message(message, vendor_id, product_id, serial_number):
    return f'{message} with ' \
           f'vendor_id={vendor_id}, ' \
           f'product_id={product_id} and ' \
           f'serial_number={serial_number}'


class ReaderNotFound(Exception):
    def __init__(self, vendor_id, product_id, serial_number):
        super(ReaderNotFound, self).__init__(
            format_reader_message('No RFID Reader found', vendor_id, product_id, serial_number)
        )


class ReaderCouldNotConnect(Exception):
    def __init__(self, reader_port, error):
        super(ReaderCouldNotConnect, self).__init__(
            format_reader_port_message('Could not connect to reader', reader_port, error)
        )
