FROM python:3.10

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./harmonica-sensor-reader /opt/harmonica-sensor-reader

WORKDIR /opt/harmonica-sensor-reader
CMD [ "python3", "main.py" ]
