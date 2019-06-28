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

    # start with a random track, then try with each of the others as last track
    random_first_filename, random_first_track = random.choice(list(meta.tracks.items()))
    all_last_tracks = [(filename, track) for (filename, track) in meta.tracks.items() if filename != random_first_filename]

    playlists = []
    print('\n⚙   Building and comparing playlists...')
    print('  › Starting with: ' + random_first_filename + '\n')

    for last_filename, last_track in all_last_tracks:
        print('  › Ending with: ' + last_filename)

        playlist = meta.create_playlist(sys.argv[1], random_first_track, last_track)
        if playlist:
            playlists.append(playlist)
            print('    » ' + str(len(playlist.tracks)) + ' tracks.\n')
        else:
            print('    » No possible playlist in this case.\n')

    # save the longest playlist
    if playlists:
        longest = playlists[0]
        for playlist in playlists:
            if len(playlist.tracks) > len(longest.tracks):
                longest = playlist

        longest.to_file()