class Port:
    def __init__(self, path, vendor_id, product_id, serial_number):
        self.path = path
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.serial_number = serial_number

    def __repr__(self):
        return f'<Port ' \
               f'path={self.path} ' \
               f'vendor_id={self.vendor_id} ' \
               f'product_id={self.product_id} ' \
               f'serial_number={self.serial_number} ' \
               f'>'
