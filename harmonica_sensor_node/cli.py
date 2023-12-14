import json
import logging
import os
import time
from argparse import ArgumentParser
from datetime import datetime as dt

import requests
import schedule
import serial
from harmonica_sensor_node import __VERSION__ as APP_VERSION
from pytz import timezone
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


def execute_serial(
    port: str,
    baudrate: int,
    tz: str,
    api_url: str,
    admin_secret: str,
) -> None:
    logger.info(f"Connecting to {port} in {baudrate}")
    ser = serial.Serial(port, baudrate)
    time.sleep(3)  # Wait connection established

    while True:
        r = ser.readline()

        try:
            pkt = json.loads(r.decode("ascii"))

            if (
                "light" in pkt
                and "humidity" in pkt
                and "temperature" in pkt
                and "mhz19_co2" in pkt
                and "mhz19_temperature" in pkt
            ):
                break
        except ValueError:
            logger.error(f"Retry, {r}")

    ser.close()

    now_aware = dt.now(timezone(tz))

    light = pkt["light"]
    humidity = pkt["humidity"]
    temperature = pkt["temperature"]
    mhz19_co2 = pkt["mhz19_co2"]
    mhz19_temperature = pkt["mhz19_temperature"]
    timestamp = now_aware.isoformat()

    logger.info(f"{timestamp}, {pkt}")

    save_graphql_api(
        api_url=api_url,
        admin_secret=admin_secret,
        light=light,
        humidity=humidity,
        temperature=temperature,
        mhz19_co2=mhz19_co2,
        mhz19_temperature=mhz19_temperature,
        timestamp=timestamp,
    )


def save_graphql_api(
    api_url: str,
    admin_secret: str,
    light: float,
    humidity: float,
    temperature: float,
    mhz19_co2: float,
    mhz19_temperature: float,
    timestamp: str,
) -> None:
    logger.info(f"Sending data to {api_url}")
    session = requests.Session()

    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    session.headers = {
        "content-type": "application/json",
        "x-hasura-admin-secret": admin_secret,
    }

    def insertSensorValue(key: str, value: float, timestamp: str) -> None:
        response = session.post(
            api_url,
            data=json.dumps(
                {
                    "query": """
mutation AddSensorValue(
    $key: String!
    $value: numeric!
    $timestamp: timestamptz!
) {
    sensorValue: insert_SensorValue_one(
        object: {
            key: $key
            value: $value
            timestamp: $timestamp
        }
    ) {
        id
    }
}
""",
                    "variables": {
                        "key": key,
                        "value": value,
                        "timestamp": timestamp,
                    },
                },
                ensure_ascii=False,
            ),
            timeout=(10.0, 30.0),
        )
        print(response.json())

    insertSensorValue(
        key="light",
        value=light,
        timestamp=timestamp,
    )
    insertSensorValue(
        key="humidity",
        value=humidity,
        timestamp=timestamp,
    )
    insertSensorValue(
        key="temperature",
        value=temperature,
        timestamp=timestamp,
    )
    insertSensorValue(
        key="mhz19_co2",
        value=mhz19_co2,
        timestamp=timestamp,
    )
    insertSensorValue(
        key="mhz19_temperature",
        value=mhz19_temperature,
        timestamp=timestamp,
    )


def main() -> None:
    default_port = os.environ.get("PORT") or "/dev/ttyUSB0"
    default_baudrate = os.environ.get("BAUDRATE") or "38400"
    default_timezone = os.environ.get("TIMEZONE") or "Asia/Tokyo"
    default_api_url = os.environ.get("API_URL") or None
    default_admin_secret = os.environ.get("ADMIN_SECRET") or None
    default_interval = os.environ.get("INTERVAL") or "900"

    parser = ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default=default_port,
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        type=int,
        default=default_baudrate,
    )
    parser.add_argument(
        "-t",
        "--timezone",
        type=str,
        default=default_timezone,
    )
    parser.add_argument(
        "--api_url",
        type=str,
        default=default_api_url,
        required=default_api_url is None,
    )
    parser.add_argument(
        "--admin_secret",
        type=str,
        default=default_admin_secret,
        required=default_admin_secret is None,
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=default_interval,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=APP_VERSION,
    )
    args = parser.parse_args()

    port: str = args.port
    baudrate: int = args.baudrate
    timezone: str = args.timezone
    api_url: str = args.api_url
    admin_secret: str = args.admin_secret
    interval: int = args.interval

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    def call() -> None:
        execute_serial(
            port=port,
            baudrate=baudrate,
            tz=timezone,
            api_url=api_url,
            admin_secret=admin_secret,
        )

    logger.info(f"Interval: {interval} s")

    call()

    schedule.every(interval).seconds.do(call)

    while True:
        schedule.run_pending()
        time.sleep(1)
