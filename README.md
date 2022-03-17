# Harmonica Sensor Reader

Create `.env`.

```env
HOST_PORT=/dev/ttyUSB0
HOST_DATA_DIR=./data
INTERVAL=300
API_URL=http://127.0.0.1:8080/v1/graphql
ADMIN_SECRET=myadminsecretkey
```

|key|value|
|:--|:--|
|HOST_PORT|Arduino Serial device path|
|HOST_DATA_DIR|Local data/db path|
|INTERVAL|Interval by the second|
|API_URL|Hasura GraphQL API endpoint|
|ADMIN_SECRET|Hasura admin secret|
