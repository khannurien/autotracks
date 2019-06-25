# autotracks
🎶 Generate automatic playlists according to your tracks' mood and groove

## Dependencies
You will need to build [bpm-tools](http://www.pogo.org.uk/~mark/bpm-tools/), [libKeyFinder](https://github.com/ibsh/libKeyFinder) and [keyfinder-cli](https://github.com/EvanPurkhiser/keyfinder-cli).

Here is a list of the dependencies that you will require during the build process:

  * sox
  * ffmpeg
  * qt5-default
  * libfftw3-dev
  * libavutil-dev
  * libavcodec-dev
  * libavformat-dev

## Usage
Edit `extract.sh` to reflect the actual paths for `keyfinder-cli` and `bpm-tag` on your system.

Use `pipenv` to enter a correct virtual environment (read Pipfile for dependencies):

```
cd autotracks
pipenv install
pipenv shell
```

Call `autotracks` with a playlist name and a list of files:

```
python run.py "my_playlist" tracks/*
```

That will create a `my_playlist.m3u` file in the current directory.
