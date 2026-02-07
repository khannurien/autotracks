# autotracks

🎶 Generate automatic playlists that follow your tracks' mood and groove

## Dependencies

You will need to build [bpm-tools](https://www.pogo.org.uk/~mark/bpm-tools/), [libkeyfinder](https://github.com/mixxxdj/libKeyFinder) and [keyfinder-cli](https://github.com/EvanPurkhiser/keyfinder-cli).

Here is a list of the dependencies that are required to build Autotracks and its dependencies:

  * `build-essential`
  * `cmake`
  * `git`
  * `libfftw3-dev`
  * `libavutil-dev`
  * `libavcodec-dev`
  * `libavformat-dev`

Runtime dependencies are as follows:

  * `ffmpeg`
  * `flac`
  * `id3v2`
  * `sox`
  * `vorbis-tools`

## Usage

### Method 1: Docker

A very naive Dockerfile is provided within the repository. It will produce a whopping ~850 MB image -- which clearly leaves room for improvement :-)

1. Build the image:

```sh
git clone https://github.com/khannurien/autotracks.git
cd autotracks
docker build \
  --build-arg UID=$(id -u) \
  --build-arg GID=$(id -g) \
  -t autotracks .
```

2. Run the image:

```sh
sudo docker run -v /path/to/audio/files:/tracks -v /path/to/save/playlist:/output autotracks
```

If Autotracks runs successfully, this will:

- recursively look for audio files under `/path/to/audio/files` and create a corresponding `.meta` file alongside each audio file if it doesn't exist yet;
- recursively look for `.meta` files under `/path/to/audio/files` and parse tracks metadata from them;
- create a `playlist.m3u` file under the `/path/to/save/playlist` directory.

### Method 2: Host

Environment variables can be used to set custom paths to `keyfinder-cli` and `bpm-tag` if necessary.
Copy `example.env` to `.env` and edit it to reflect your system's configuration, or set and export the variables from your shell before launching Autotracks.

You can use `uv` to initialize a correct virtual environment (read `pyproject.toml` for Python dependencies):

```sh
git clone https://github.com/khannurien/autotracks.git
cd autotracks
uv sync
```

Call Autotracks with a playlist name and a directory or a list of files:

```sh
uv run python -m src.autotracks "my_playlist.m3u" tracks/
```

This will create a `my_playlist.m3u` file in the current directory.

If some tracks remain unused or generate errors, their names will be displayed after playlist generation. You can then append them manually to the playlist if you wish.

Note: Autotracks creates a `.meta` file alongside each track of the list. These files contain the track key and BPM and are not removed after generation, in order to keep audio analysis results cached for further work. They can be safely removed should you not need them anymore.

## Development

Run tests:

```sh
uv sync
uv run python -m pytest
```
