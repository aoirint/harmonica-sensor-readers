# Harmonica Sensor Node

## Links

- GitHub: <https://github.com/aoirint/harmonica_sensor_node>
- Docker Hub: <https://hub.docker.com/r/aoirint/harmonica_sensor_node>

## Supported sensor device

- <https://github.com/aoirint/HomeSensorIno>

## Development guide

- Python 3.11

ライブラリ管理に[Poetry](https://python-poetry.org/docs/#installation)を使っています。

```shell
poetry install

poetry run python scripts/main.py --help

poetry run pysen run lint
poetry run pysen run format

poetry export --without-hashes -o requirements.txt
poetry export --without-hashes --with dev -o requirements-dev.txt
```

## Environment variables

Create `.env`.

```env
HOST_PORT=/dev/ttyUSB0
HOST_DIALOUT_GID=20
INTERVAL=300
API_URL=http://hasura:8080/v1/graphql
ADMIN_SECRET=myadminsecretkey
```

|key|value|
|:--|:--|
|HOST_PORT|Arduino Serial device path (UID:GID = root:dialout)|
|HOST_DIALOUT_GID| `getent group dialout \| cut -d: -f3` |
|INTERVAL|Interval by the second|
|API_URL|Hasura GraphQL API endpoint|
|ADMIN_SECRET|Hasura admin secret|
