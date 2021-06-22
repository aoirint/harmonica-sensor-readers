FROM python:3

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

WORKDIR /code

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./src /code

CMD [ "python3", "main.py" ]
