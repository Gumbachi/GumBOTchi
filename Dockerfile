
FROM python:3.11-slim-bullseye

RUN apt-get -qq update
RUN apt-get install -y ffmpeg --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt *.env ./

RUN pip3 install -r requirements.txt

RUN apt-get autoremove

COPY src ./src

CMD [ "python3", "src/main.py" ]