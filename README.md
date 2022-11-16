# Harmonica Sensor Reader

Create `.env`.

```env
HOST_PORT=/dev/ttyUSB0
HOST_DATA_DIR=./data
HOST_DIALOUT_GID=20
INTERVAL=300
API_URL=http://hasura:8080/v1/graphql
ADMIN_SECRET=myadminsecretkey
```

|key|value|
|:--|:--|
|HOST_PORT|Arduino Serial device path|
|HOST_DATA_DIR|Local data/db path（Harmonicaが安定稼働するまでの暫定的なHomeSensorPy相当機能の維持）|
|HOST_DIALOUT_GID|`getent group dialout | cut -d: -f3`|
|INTERVAL|Interval by the second|
|API_URL|Hasura GraphQL API endpoint|
|ADMIN_SECRET|Hasura admin secret|
