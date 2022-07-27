# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

RUN pip3 install flask

COPY simple_size_server.py main.py

CMD [ "python3", "main.py" ]