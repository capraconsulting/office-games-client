import json
import os

import datetime

from app.utils.firebase import get_firebase


def backup():
    db = get_firebase().database()
    if not os.path.exists('backups'):
        os.makedirs('backups')
    backup_file = f'backups/backup-{datetime.datetime.now():%Y%m%d_%H%M%S}.json'
    f = open(backup_file, 'w')
    f.write(json.dumps(db.get().val()))
    f.close()
    print(f'Backup saved: {backup_file}')
