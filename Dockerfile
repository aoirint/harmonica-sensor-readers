# syntax=docker/dockerfile:1.4
FROM python:3.11

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

ADD ./harmonica-sensor-reader /opt/harmonica-sensor-reader

ADD ./entrypoint.sh /
ENTRYPOINT [ "/entrypoint.sh" ]

WORKDIR /opt/harmonica-sensor-reader
CMD [ "gosu", "user", "python3", "main.py" ]
