# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY src .
COPY config.toml config.toml

CMD [ "python3", "main.py" ]