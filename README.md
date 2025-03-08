# autotracks

🎶 Generate automatic playlists according to your tracks' mood and groove

## Dependencies

You will need to build [bpm-tools](https://www.pogo.org.uk/~mark/bpm-tools/), [libkeyfinder](https://github.com/mixxxdj/libKeyFinder) and [keyfinder-cli](https://github.com/EvanPurkhiser/keyfinder-cli).

Here is a list of the dependencies that you will require to build Autotracks and its dependencies:

  * `build-essential`
  * `cmake`
  * `ffmpeg`
  * `git`
  * `libfftw3-dev`
  * `libavutil-dev`
  * `libavcodec-dev`
  * `libavformat-dev`
  * `sox`

Runtime dependencies are as follows:

  * `ffmpeg`
  * `flac`
  * `id3v2`
  * `vorbis-tools`
  * `sox`

## Usage

### Method 1: Docker

A very naive Dockerfile is provided within the repository. It will produce a whopping ~850 MB image -- which clearly leaves room for improvement :-)

1. Build the image:

```sh
git clone https://github.com/khannurien/autotracks.git
cd autotracks
sudo docker build -t autotracks .
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

Edit `extract.sh` to reflect the actual paths for `keyfinder-cli` and `bpm-tag` on your system.

Use `pipenv` to enter a correct virtual environment (read `Pipfile` for Python dependencies):

```sh
git clone https://github.com/khannurien/autotracks.git
cd autotracks
pipenv install
```

Call Autotracks with a playlist name and a directory or a list of files:

```sh
pipenv run python3 -m src.autotracks "my_playlist.m3u" tracks/
```

This will create a `my_playlist.m3u` file in the current directory.

If some tracks remain unused or generate errors, their names will be displayed after playlist generation. You can then append them manually to the playlist if you wish.

Note: Autotracks creates a `.meta` file alongside each track of the list. These files contain the track key and BPM and are not removed after generation, in order to keep audio analysis results cached for further work. They can be safely removed should you not need them anymore.

## Development

Run tests:

```sh
pipenv install --dev
pipenv run python3 -m pytest
```

## Performance

Autotracks is a single-threaded application. Using threads to divide the problem would greatly improve performance.

On an Intel i5-2400 CPU @ 3.10GHz, sorting a folder containing 317 tracks takes approximately 37 minutes, including audio analysis.

In that test case, only one track remained unused, and 3 produced errors (raised by `keyfinder-cli` for reasons yet unknown).
