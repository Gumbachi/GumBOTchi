FROM python:3.11-slim-bullseye

RUN apt-get update \
    && apt-get install -y ffmpeg --no-install-recommends \
    && apt-get install -y chromium-driver \
    && apt-get install -y supervisor \
    && pip3 install poetry \
    && rm -rf /var/lib/apt/lists/* \
    && poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock *.env ./
RUN poetry install --no-dev

COPY src ./src
COPY src/supervisor.conf /etc/supervisor/conf.d/supervisord.conf

ENTRYPOINT ["/usr/bin/supervisord"]
# ENTRYPOINT python3 src/main.py