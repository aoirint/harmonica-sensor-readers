# syntax=docker/dockerfile:1.6
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
EOF

RUN <<EOF
    set -eu

    groupadd -g 2000 user
    useradd -m -o -u 2000 -g user user
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/harmonica_sensor_node
    chown -R "user:user" /code/harmonica_sensor_node

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "user:user" /home/user/.cache
EOF

ADD ./pyproject.toml ./poetry.lock /code/harmonica_sensor_node/
ARG POETRY_VERSION=1.7.1
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"
EOF

WORKDIR /code/harmonica_sensor_node
RUN --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --only main
EOF

ADD ./harmonica_sensor_node /code/harmonica_sensor_node/harmonica_sensor_node

ADD ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "gosu", "user", "poetry", "run", "python", "-m", "harmonica_sensor_node" ]
