import serial
import time
import json

from datetime import datetime as dt
from pytz import timezone

from pathlib import Path
import sqlite3

import logging
logger = logging.getLogger(__name__)


def execute(
    port: str,
    baudrate: int,
    tz: str,
    db_path: Path,
):
    ser = serial.Serial(port, baudrate)
    time.sleep(3) # Wait connection established

    while True:
        r = ser.readline()

        try:
            pkt = json.loads(r.decode('ascii'))

            if 'light' in pkt and 'humidity' in pkt and 'temperature' in pkt:
                break
        except:
            logger.error(f'Retry, {r}')
            pass

    ser.close()


    now_aware = dt.now(timezone(tz))

    light = pkt['light']
    humidity = pkt['humidity']
    temperature = pkt['temperature']
    timestamp = now_aware.isoformat()

    logger.info(f'{timestamp}, {pkt}')

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS sensor(id INTEGER PRIMARY KEY AUTOINCREMENT, light INTEGER, humidity INTEGER, temperature INTEGER, timestamp DATETIME)')

    cur.execute('INSERT INTO sensor VALUES(?,?,?,?,?)', (None, light, humidity, temperature, timestamp, ))

    db.commit()
    db.close()


if __name__ == '__main__':
    import configargparse as argparse
    parser = argparse.ArgumentParser()
    parser.add('-p', '--port', env_var='PORT', type=str, default='/dev/ttyUSB0')
    parser.add('-b', '--baudrate', env_var='BAUDRATE',type=int, default=38400)
    parser.add('-t', '--timezone', env_var='TIMEZONE',type=str, default='Asia/Tokyo')
    parser.add('-o', '--db_path', env_var='DB_PATH',type=str, default='data/sensordb.sqlite3')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    def call():
        execute(
            port=args.port,
            baudrate=args.baudrate,
            tz=args.timezone,
            db_path=Path(args.db_path),
        )

    import schedule
    schedule.every(5).minutes.do(call)

    while True:
        schedule.run_pending()
        time.sleep(1)
