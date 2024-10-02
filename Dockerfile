FROM python:3.12-slim-bookworm

RUN apt update \
    && apt install -y ffmpeg --no-install-recommends \
    && pip3 install uv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

COPY src ./src

ENTRYPOINT ["uv", "run", "src/main.py"]
