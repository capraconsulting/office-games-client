#!/usr/bin/python
import sys
import os
from clint.arguments import Args

from commands.backup import backup
from commands.check_player_statistics import check_player_statistics
from commands.list_readers import list_readers
from commands.sensor_test import sensor_test
from commands.start import start

AVAILABLE_COMMANDS = [
    'backup',
    'check_player_statistics',
    'list_readers',
    'sensor_test',
    'start'
]


if __name__ == '__main__':
    # TODO: Get from ENV variable
    game_slug = 'ping-pong'
    sys.path.insert(0, os.path.abspath('..'))
    args = Args()
    if len(args) == 0 or args.all[0] not in AVAILABLE_COMMANDS:
        print(f'Unknown command. Available commands: {", ".join(AVAILABLE_COMMANDS)}')
        sys.exit(1)

    command = args.all[0].lower()

    if command == 'backup':
        backup()
    elif command == 'check_player_statistics':
        check_player_statistics(game_slug)
    elif command == 'list_readers':
        list_readers()
    elif command == 'sensor_test':
        sensor_test()
    elif command == 'start':
        start(game_slug)

    sys.exit(0)
