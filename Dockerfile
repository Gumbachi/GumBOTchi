# syntax=docker/dockerfile:1

FROM python:3.10-alpine

RUN apk add ffmpeg

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "src/main.py" ]