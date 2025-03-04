# autotracks

🎶 Generate automatic playlists according to your tracks' mood and groove

## Dependencies

You will need to build [bpm-tools](https://www.pogo.org.uk/~mark/bpm-tools/), [libkeyfinder](https://github.com/mixxxdj/libKeyFinder) and [keyfinder-cli](https://github.com/EvanPurkhiser/keyfinder-cli).

Here is a list of the dependencies that you will require during the build process:

  * `cmake`
  * `ffmpeg`
  * `libfftw3-dev`
  * `libavutil-dev`
  * `libavcodec-dev`
  * `libavformat-dev`
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

### Method 2: Host

Edit `extract.sh` to reflect the actual paths for `keyfinder-cli` and `bpm-tag` on your system.

Use `pipenv` to enter a correct virtual environment (read Pipfile for dependencies):

```sh
cd autotracks
pipenv install
pipenv shell
```

Call `autotracks` with a playlist name and a directory or a list of files:

```sh
python3 -m src.autotracks "my_playlist" tracks/
```

This will create a `my_playlist.m3u` file in the current directory.

If some tracks remain unused or generate errors, their names will be displayed after playlist generation. You can then append them manually to the playlist if you wish.

Note: `autotracks` creates a `.meta` file alongside each track of the list. These files contain the track key and BPM and are not removed after generation, in order to keep audio analysis results cached for further work. They can be safely removed should you not need them anymore.

## Performance

`autotracks` is a single-threaded application. Using threads to divide the problem would greatly improve performance.

On an Intel i5-2400 CPU @ 3.10GHz, sorting a folder containing 317 tracks takes approximately 37 minutes, including audio analysis.

In that test case, only one track remained unused, and 3 produced errors (raised by `keyfinder-cli` for reasons yet unknown).
