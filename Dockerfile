# syntax=docker/dockerfile:1.7
FROM python:3.11.9

ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/code/harmonica_sensor_node/.venv/bin:/home/user/.local/bin:${PATH}

RUN <<EOF
    set -eu

    apt-get update

    apt-get install -y \
        gosu

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

RUN <<EOF
    set -eu

    groupadd --non-unique --gid 2000 user
    useradd --non-unique --uid 2000 --gid 2000 --create-home user
EOF

ARG POETRY_VERSION=1.8.2
RUN <<EOF
    set -eu

    gosu user pip install "poetry==${POETRY_VERSION}"

    gosu user poetry config virtualenvs.in-project true

    mkdir -p /home/user/.cache/pypoetry/{cache,artifacts}
    chown -R "user:user" /home/user/.cache
EOF

RUN <<EOF
    set -eu

    mkdir -p /code/harmonica_sensor_node
    chown -R "user:user" /code/harmonica_sensor_node
EOF

WORKDIR /code/harmonica_sensor_node
ADD ./pyproject.toml ./poetry.lock /code/harmonica_sensor_node/
RUN --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --no-root --only main
EOF

ADD ./harmonica_sensor_node /code/harmonica_sensor_node/harmonica_sensor_node
ADD ./README.md /code/harmonica_sensor_node/
RUN --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/cache \
    --mount=type=cache,uid=2000,gid=2000,target=/home/user/.cache/pypoetry/artifacts <<EOF
    set -eu

    gosu user poetry install --only main
EOF

ADD ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "gosu", "user", "poetry", "run", "python", "-m", "harmonica_sensor_node" ]
