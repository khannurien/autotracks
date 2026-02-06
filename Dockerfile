FROM python:3.12-slim AS base

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
 sox

RUN mkdir /build
WORKDIR /build

RUN git clone https://github.com/mixxxdj/libkeyfinder.git && \
 cd libkeyfinder && \
 cmake -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
 cmake --build build --parallel 4 && \
 cmake --install build && \
 cd ..

RUN git clone https://github.com/EvanPurkhiser/keyfinder-cli.git && \
 cd keyfinder-cli && \
 cmake -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
 cmake --build build && \
 cmake --install build && \
 cd ..

RUN git clone https://www.pogo.org.uk/~mark/bpm-tools.git && \
 cd bpm-tools && \
 make && \
 make install && \
 cd ..

RUN python3 -m pip install python-dotenv python-magic pytest pytest-datadir ruff

COPY ./src /app/src

WORKDIR /app

VOLUME ["/tracks"]
VOLUME ["/output"]

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV LD_LIBRARY_PATH="/usr/local/lib"

ENTRYPOINT ["python3", "-m", "src.autotracks", "/output/playlist.m3u", "/tracks"]

# FROM python:3.12-slim as base

# # Setup env
# ENV LANG=C.UTF-8
# ENV LC_ALL=C.UTF-8
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONFAULTHANDLER=1

# FROM base AS builder

# # Install build dependencies
# RUN apt-get update && \
#  apt-get install -y \
#  build-essential \
#  cmake \
#  git \
#  libavcodec-dev \
#  libavformat-dev \
#  libavutil-dev \
#  libfftw3-dev

# # Install pipenv
# RUN pip install pipenv

# # Install python dependencies in /.venv
# COPY Pipfile .
# COPY Pipfile.lock .
# RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

# # Build dependencies
# RUN git clone https://github.com/mixxxdj/libkeyfinder.git && \
#  cd libkeyfinder && \
#  cmake -DBUILD_SHARED_LIBS=OFF -DCMAKE_INSTALL_PREFIX=/usr/local -S . -B build && \
#  cmake --build build --parallel 4 && \
#  cmake --install build && \
#  cd ..

# RUN git clone https://github.com/EvanPurkhiser/keyfinder-cli.git && \
#  cd keyfinder-cli && \
#  make && \
#  make install && \
#  cd ..

# RUN git clone https://www.pogo.org.uk/~mark/bpm-tools.git && \
#  cd bpm-tools && \
#  make && \
#  make install && \
#  cd ..

# FROM base AS runner

# # Install runtime dependencies
# RUN apt-get update && \
#  apt-get install -y \
#  ffmpeg \
#  flac \
#  id3v2 \
#  sox \
#  vorbis-tools

# # Create new user
# RUN useradd --create-home app

# # Copy virtual env from builder stage
# COPY --from=builder --chown=app:app /.venv /.venv
# ENV PATH="/.venv/bin:$PATH"

# # Switch to new user
# USER app
# WORKDIR /home/app

# # Persistent volumes for output files
# RUN mkdir /tracks
# RUN mkdir /output
# VOLUME ["/tracks"]
# VOLUME ["/output"]

# # Copy dependencies from builder stage
# COPY --from=builder /usr/local/lib/libkeyfinder

# # Install application into container
# COPY --chown=app:app ./src /app/src

# # Run autotracks
# ENTRYPOINT ["python3", "-m", "src.autotracks", "/output/playlist", "/tracks"]
