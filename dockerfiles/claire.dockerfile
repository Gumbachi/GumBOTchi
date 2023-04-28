FROM python:3.11-slim-bullseye

RUN apt-get update \
    && apt-get install -y chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY *.env ./

COPY src/ ./src

RUN pip3 install -r src/cogs/claire/api/requirements.txt

EXPOSE 80
ENTRYPOINT python3 -u src/cogs/claire/api/server.py