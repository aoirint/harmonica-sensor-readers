FROM python:3

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

WORKDIR /work

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./main.py /work/
ADD ./graph /work/graph

CMD [ "python3", "main.py" ]
