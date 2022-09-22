# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y ffmpeg gcc g++ --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN apt-get purge -y --auto-remove gcc g++

COPY . .

CMD [ "python3", "src/main.py" ]