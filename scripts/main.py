import json
import logging
import time
from datetime import datetime as dt

import configargparse as argparse
import requests
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add("-p", "--port", env_var="PORT", type=str, default="/dev/ttyUSB0")
    parser.add("-b", "--baudrate", env_var="BAUDRATE", type=int, default=38400)
    parser.add("-t", "--timezone", env_var="TIMEZONE", type=str, default="Asia/Tokyo")
    parser.add("--api_url", env_var="API_URL", type=str, required=True)
    parser.add("--admin_secret", env_var="ADMIN_SECRET", type=str, required=True)
    parser.add("-i", "--interval", env_var="INTERVAL", type=int, default=15 * 60)
    parser.add(
        "--version",
        action="version",
        version=APP_VERSION,
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s : %(message)s",
    )

    def call() -> None:
        execute_serial(
            port=args.port,
            baudrate=args.baudrate,
            tz=args.timezone,
            api_url=args.api_url,
            admin_secret=args.admin_secret,
        )

    logger.info(f"Interval: {args.interval} s")

    call()

    import schedule

    schedule.every(args.interval).seconds.do(call)

    while True:
        schedule.run_pending()
        time.sleep(1)
