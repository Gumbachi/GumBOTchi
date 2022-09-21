# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY . .

CMD [ "python3", "src/main.py" ]