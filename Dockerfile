
FROM python:3.11-slim-bullseye

RUN apt-get -qq update \
    && apt-get install -y ffmpeg --no-install-recommends \
    && pip3 install poetry \
    && rm -rf /var/lib/apt/lists/* \
    && poetry config virtualenvs.create false

RUN apt-get update
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

WORKDIR /app

COPY pyproject.toml poetry.lock *.env ./
RUN poetry install --no-dev

# RUN apt-get autoremove

COPY src ./src

ENTRYPOINT ["python3", "src/main.py"]