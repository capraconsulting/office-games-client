class Port:
    def __init__(self, path, vendor_id, product_id, serial_number, physical_port=None):
        self.path = path
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial_number = serial_number
        self.physical_port = physical_port

    def __repr__(self):
        return f'<Port ' \
               f'path={self.path} ' \
               f'vendor_id={self.vendor_id} ' \
               f'product_id={self.product_id} ' \
               f'serial_number={self.serial_number} ' \
               f'physical_port={self.physical_port} ' \
               f'>'
