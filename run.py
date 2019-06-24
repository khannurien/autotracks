#/usr/bin/env python
# coding: utf-8

import random
import sys

import autotracks
from autotracks import track, playlist, library

if __name__ == '__main__':
    meta = library.Library()
    meta.add(sys.argv[1:])

    random_first_filename, random_first_track = random.choice(list(meta.tracks.items()))
    random_last_filename, random_last_track = random.choice(list(meta.tracks.items()))
    print("start with: " + random_first_filename)
    print("end with: " + random_last_filename)

    playlist = meta.create_playlist('coucou', random_first_track, random_last_track)
    playlist.to_file()