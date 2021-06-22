FROM python:3

WORKDIR /work

ADD ./requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./main.py /work/

CMD [ "python3", "main.py" ]
