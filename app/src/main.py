import serial
import time
import json

from datetime import datetime as dt
from pytz import timezone

from pathlib import Path
import sqlite3

import logging
logger = logging.getLogger(__name__)


def execute_serial(
    port: str,
    baudrate: int,
    tz: str,
    db_path: Path,
):
    logger.info(f'Connecting to {port} in {baudrate}')
    ser = serial.Serial(port, baudrate)
    time.sleep(3) # Wait connection established

    while True:
        r = ser.readline()

        try:
            pkt = json.loads(r.decode('ascii'))

            if 'light' in pkt and 'humidity' in pkt and 'temperature' in pkt and 'mhz19_co2' in pkt and 'mhz19_temperature' in pkt:
                break
        except:
            logger.error(f'Retry, {r}')
            pass

    ser.close()


    now_aware = dt.now(timezone(tz))

    light = pkt['light']
    humidity = pkt['humidity']
    temperature = pkt['temperature']
    mhz19_co2 = pkt['mhz19_co2']
    mhz19_temperature = pkt['mhz19_temperature']
    timestamp = now_aware.isoformat()

    logger.info(f'{timestamp}, {pkt}')

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS sensor(id INTEGER PRIMARY KEY AUTOINCREMENT, light INTEGER, humidity INTEGER, temperature INTEGER, mhz19_co2 INTEGER, mhz19_temperature INTEGER, timestamp DATETIME)')

    cur.execute('INSERT INTO sensor VALUES(?,?,?,?,?,?,?)', (None, light, humidity, temperature, mhz19_co2, mhz19_temperature, timestamp, ))

    db.commit()
    db.close()


def execute_graph(
    tz: str,
    graph_dir: Path,
    db_path: Path,
):
    from graph.light import draw_days as draw_light
    from graph.humidity import draw_days as draw_humidity
    from graph.temperature import draw_days as draw_temperature
    from graph.mhz19_co2 import draw_days as draw_mhz19_co2
    from graph.mhz19_temperature import draw_days as draw_mhz19_temperature

    db = sqlite3.connect(db_path)
    cur = db.cursor()

    draw_light(
        cur=cur,
        output_dir=graph_dir / 'light',
        tz=tz,
        days=1,
    )

    draw_humidity(
        cur=cur,
        output_dir=graph_dir / 'humidity',
        tz=tz,
        days=1,
    )

    draw_temperature(
        cur=cur,
        output_dir=graph_dir / 'temperature',
        tz=tz,
        days=1,
    )
    
    draw_mhz19_co2(
        cur=cur,
        output_dir=graph_dir / 'mhz19_co2',
        tz=tz,
        days=1,
    )
    
    draw_mhz19_temperature(
        cur=cur,
        output_dir=graph_dir / 'mhz19_temperature',
        tz=tz,
        days=1,
    )

    db.close()


if __name__ == '__main__':
    import configargparse as argparse
    parser = argparse.ArgumentParser()
    parser.add('-p', '--port', env_var='PORT', type=str, default='/dev/ttyUSB0')
    parser.add('-b', '--baudrate', env_var='BAUDRATE', type=int, default=38400)
    parser.add('-t', '--timezone', env_var='TIMEZONE', type=str, default='Asia/Tokyo')
    parser.add('-o', '--db_path', env_var='DB_PATH', type=str, default='data/sensordb.sqlite3')
    parser.add('-g', '--graph_dir', env_var='GRAPH_DIR', type=str, default='data/graph')
    parser.add('-i', '--interval', env_var='INTERVAL', type=int, default=15*60)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s : %(message)s',
    )

    def call():
        execute_serial(
            port=args.port,
            baudrate=args.baudrate,
            tz=args.timezone,
            db_path=Path(args.db_path),
        )
        execute_graph(
            tz=args.timezone,
            graph_dir=Path(args.graph_dir),
            db_path=Path(args.db_path),
        )

    logger.info(f'Interval: {args.interval} s')

    call()

    import schedule
    schedule.every(args.interval).seconds.do(call)

    while True:
        schedule.run_pending()
        time.sleep(1)
