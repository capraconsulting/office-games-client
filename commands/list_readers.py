import evdev


def list_readers():
    print('Printing available devices:')
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    for device in devices:
        print(f'fd = {device.fd}')
        print(f'fn = {device.fn}')
        print(f'name = {device.name}')
        print(f'phys = {device.phys}')
        print(f'info = {device.info}')
        print(f'version = {device.version}')
        print('-------------------------------------------')
