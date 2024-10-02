FROM python:3.12-slim-bullseye

RUN apt-get update \
    && apt-get install -y ffmpeg --no-install-recommends \
    && apt-get install -y chromium-driver \
    && pip3 install uv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

# RUN uv sync

COPY src ./src

ENTRYPOINT uv run src/main.py
