FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libfftw3-dev \
    pkg-config \
    ca-certificates

RUN pip install --no-cache-dir uv

WORKDIR /build

RUN git clone https://github.com/mixxxdj/libkeyfinder.git && \
    cd libkeyfinder && \
    cmake -DBUILD_SHARED_LIBS=OFF -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
    cmake --build build --parallel $(nproc) && \
    cmake --install build && \
    cd .. && \
    rm -rf libkeyfinder

RUN git clone https://github.com/EvanPurkhiser/keyfinder-cli.git && \
    cd keyfinder-cli && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
    cmake --build build --parallel $(nproc) && \
    cmake --install build && \
    cd .. && \
    rm -rf keyfinder-cli

RUN git clone https://www.pogo.org.uk/~mark/bpm-tools.git && \
    cd bpm-tools && \
    make && \
    make install && \
    cd .. && \
    rm -rf bpm-tools

COPY pyproject.toml uv.lock /app/

WORKDIR /app

RUN uv sync --frozen --no-dev
RUN uv export --frozen --format requirements-txt > requirements.txt

FROM python:3.11-slim AS runtime

ARG UID=1000
ARG GID=1000

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    flac \
    id3v2 \
    sox \
    vorbis-tools \
    libmagic1 \
    libfftw3-bin \
    libavcodec61 \
    libavformat61 \
    libavutil59 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID} app && \
    useradd --create-home --shell /bin/bash --uid ${UID} --gid ${GID} app && \
    mkdir -p /app /tracks /output /app/log && \
    chown -R app:app /app /tracks /output

COPY --from=builder /usr/local/bin/keyfinder-cli /usr/local/bin/keyfinder-cli
COPY --from=builder /usr/local/bin/bpm /usr/local/bin/bpm
COPY --from=builder /usr/local/bin/bpm-tag /usr/local/bin/bpm-tag

COPY --chown=app:app --from=builder /app/requirements.txt /app/
COPY --chown=app:app src /app/src

RUN pip install -r /app/requirements.txt

USER app
WORKDIR /app

VOLUME ["/tracks", "/output"]

ENTRYPOINT ["python", "-m", "src.autotracks", "/output/playlist.m3u", "/tracks"]
