import serial
import time
import json

from datetime import datetime as dt
from pytz import timezone

import sqlite3


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=str, default='/dev/ttyACM0')
    parser.add_argument('-b', '--baudrate', type=int, default=38400)
    parser.add_argument('-t', '--timezone', type=str, default='Asia/Tokyo')
    args = parser.parse_args()

    tz = args.timezone

    ser = serial.Serial(args.port, args.baudrate)
    time.sleep(3) # Wait connection established

    while True:
        r = ser.readline()

        try:
            pkt = json.loads(r.decode('ascii'))

            if 'light' in pkt and 'humidity' in pkt and 'temperature' in pkt:
                break
        except:
            print('Retry, %s' % r)
            pass

    ser.close()


    now_aware = dt.now(timezone(tz))

    light = pkt['light']
    humidity = pkt['humidity']
    temperature = pkt['temperature']
    timestamp = now_aware.isoformat()

    print(timestamp, pkt)


    db = sqlite3.connect('sensordb.sqlite3')
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS sensor(id INTEGER PRIMARY KEY AUTOINCREMENT, light INTEGER, humidity INTEGER, temperature INTEGER, timestamp DATETIME)')

    cur.execute('INSERT INTO sensor VALUES(?,?,?,?,?)', (None, light, humidity, temperature, timestamp, ))

    db.commit()
    db.close()
