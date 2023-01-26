FROM docker.io/python:3.8-alpine

ADD ./main.py /main.py
ADD ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

ENTRYPOINT python3 /main.py
