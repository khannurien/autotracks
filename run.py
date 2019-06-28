#/usr/bin/env python
# coding: utf-8

import random
import os
import sys

import autotracks
from autotracks import track, playlist, library

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: {autotracks} {playlist} {tracks}'
            .format(
                autotracks=sys.argv[0],
                playlist='<playlist name>',
                tracks='<track list>'
            )
        )
        sys.exit(1)

    meta = library.Library()
    tracks = []

    if os.path.isdir(sys.argv[2]):
        for (path, directories, filenames) in os.walk(sys.argv[2]):
            # prepend the path to filenames
            tracks.extend(os.path.join(path, filename) for filename in filenames)
            break
    else:
        tracks = sys.argv[2:]
    
    meta.add(tracks)

    if len(meta.tracks) < 2:
        print('Not enough tracks in list.')
        sys.exit(1)

    # TODO we need to maximize playlist size by choosing the best fitted starting and ending tracks
    random_first_filename, random_first_track = random.choice(list(meta.tracks.items()))
    random_last_filename, random_last_track = random.choice(list(meta.tracks.items()))
    print('\n⚙   Started building playlist...')
    print('  › Starting with: ' + random_first_filename)
    print('  › Ending with: ' + random_last_filename + '\n')

    playlist = meta.create_playlist(sys.argv[1], random_first_track, random_last_track)
    if playlist:
        playlist.to_file()
    else:
        print('No playlist generated during this run. Try again!')