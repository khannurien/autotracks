FROM python:3.11-slim AS base

ARG UID=1000
ARG GID=1000

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    ffmpeg \
    flac \
    id3v2 \
    vorbis-tools \
    git \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libfftw3-dev \
    pkg-config \
    sox && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /build

RUN git clone https://github.com/mixxxdj/libkeyfinder.git && \
    cd libkeyfinder && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
    cmake --build build --parallel 4 && \
    cmake --install build && \
    cd .. && \
    rm -rf libkeyfinder

RUN git clone https://github.com/EvanPurkhiser/keyfinder-cli.git && \
    cd keyfinder-cli && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
    cmake --build build && \
    cmake --install build && \
    cd .. && \
    rm -rf keyfinder-cli

RUN git clone https://www.pogo.org.uk/~mark/bpm-tools.git && \
    cd bpm-tools && \
    make && \
    make install && \
    cd .. && \
    rm -rf bpm-tools

RUN groupadd --gid ${GID} app && \
    useradd --create-home --shell /bin/bash --uid ${UID} --gid ${GID} app && \
    mkdir -p /app /tracks /output /app/log && \
    chown -R app:app /app /tracks /output

USER app

VOLUME ["/tracks"]
VOLUME ["/output"]

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    LD_LIBRARY_PATH="/usr/local/lib"
