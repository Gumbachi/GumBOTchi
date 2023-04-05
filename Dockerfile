FROM python:3.11-slim-bullseye

RUN apt-get -qq update \
    && apt-get install -y ffmpeg --no-install-recommends \
    && pip3 install poetry \
    && rm -rf /var/lib/apt/lists/* \
    && poetry config virtualenvs.create false

RUN apt-get update
RUN apt-get install -y chromium-driver

WORKDIR /app

COPY pyproject.toml poetry.lock *.env ./
RUN poetry install --no-dev

COPY src ./src

ENTRYPOINT ["python3", "src/main.py"]