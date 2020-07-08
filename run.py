#/usr/bin/env python
# coding: utf-8

import random
import os
import sys

import autotracks
from autotracks import track, playlist, library, tools
from autotracks.errors import NotEnoughTracksError

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: {autotracks} {playlist} {tracks}'
            .format(
                autotracks=sys.argv[0],
                playlist='<playlist name>',
                tracks='<track list>'
            )
        )
        sys.exit(1)

    # initialize library
    autotracks = tools.Autotracks(sys.argv[1])
    try:
        autotracks.load(sys.argv[2:])
    except NotEnoughTracksError as error:
        print(error.message)
        sys.exit(2)

    # generate playlists and save the longest
    autotracks.generate()
    longest = autotracks.save_longest_playlist()

    # show unused tracks
    autotracks.show_unused_tracks(longest)

    # show errors
    autotracks.show_errors()

