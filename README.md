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

A very naive Dockerfile is provided within the repository. It will produce a whooping ~850 MB image which clearly leaves room for improvement :-)

```
git clone https://github.com/khannurien/autotracks.git
cd autotracks
sudo docker build -t autotracks .
sudo docker run -v /path/to/audio/files:/tracks -v /path/to/save/playlist:/output autotracks
```

## Usage
Edit `extract.sh` to reflect the actual paths for `keyfinder-cli` and `bpm-tag` on your system.

Use `pipenv` to enter a correct virtual environment (read Pipfile for dependencies):

```
cd autotracks
pipenv install
pipenv shell
```

Call `autotracks` with a playlist name and a directory or a list of files:

```
python run.py "my_playlist" tracks/
```

That will create a `my_playlist.m3u` file in the current directory.

If tracks remain unused or produced errors, they will be displayed after playlist generation. You can then append them manually to the playlist if you wish.

Note: `autotracks` create a `.meta` file alongside each track of the list. These files contain the track key and BPM and are not removed after generation, in order to keep audio analysis results for further work. They can be safely removed should you not need them anymore.

## Performance
`autotracks` is a single-threaded application. Using threads to divide the problem would greatly improve performance.

On an Intel i5-2400 CPU @ 3.10GHz, sorting a folder containing 317 tracks takes approximately 37 minutes, including audio analysis.

In that test case, only one track remained unused, and 3 produced errors (raised by `keyfinder-cli` for reasons yet unknown).

