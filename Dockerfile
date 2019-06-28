FROM ubuntu:18.04

RUN apt-get update && \
 apt-get install -y \
 build-essential \
 ffmpeg \
 git \
 libavcodec-dev \
 libavformat-dev \
 libavutil-dev \
 libfftw3-dev \
 python3 \
 python3-pip \
 qt5-default \
 sox

RUN pip3 install filetype

RUN mkdir /build
WORKDIR /build

RUN git clone https://github.com/ibsh/libKeyFinder.git && \
 cd libKeyFinder && \
 qmake && \
 make && \
 make install && \
 cd ..

RUN git clone https://github.com/EvanPurkhiser/keyfinder-cli.git && \
 cd keyfinder-cli && \
 make && \
 make install && \
 cd ..

RUN git clone http://www.pogo.org.uk/~mark/bpm-tools.git && \
 cd bpm-tools && \
 make && \
 make install && \
 cd ..

RUN git clone https://github.com/khannurien/autotracks.git /app

WORKDIR /app

VOLUME ["/tracks"]
VOLUME ["/output"]

ENV LANG C.UTF-8

ENTRYPOINT ["python3", "run.py", "/output/playlist", "/tracks"]
