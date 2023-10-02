# syntax=docker/dockerfile:1.5
FROM python:3.11

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/user/.local/bin:${PATH}

RUN <<EOF
    apt-get update
    apt-get install -y \
        gosu
    apt-get clean
    rm -rf /var/lib/apt/lists/*

    groupadd -g 2000 user
    useradd -m -o -u 2000 -g user user
EOF

ADD ./requirements.txt /tmp/
RUN gosu user pip3 install -r /tmp/requirements.txt

ADD ./scripts /code
ADD ./harmonica_sensor_node /code/harmonica_sensor_node

ADD ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "gosu", "user", "python3", "/code/main.py" ]
