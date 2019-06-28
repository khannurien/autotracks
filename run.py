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

    # add all tracks from the given directory or list in the library
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

    # explore every graph for the track list and generate every playlist
    playlists = []
    for first_filename, first_track in meta.tracks.items():
        print('\n⚙   Building and comparing playlists...')
        print('  › Starting with: ' + first_filename + '\n')

        all_last_tracks = [(filename, track) for (filename, track) in meta.tracks.items() if filename != first_filename]
        for last_filename, last_track in all_last_tracks:
            print('  › Ending with: ' + last_filename)

            playlist = meta.create_playlist(sys.argv[1], first_track, last_track)
            if playlist:
                playlists.append(playlist)
                print('    » ' + str(len(playlist.tracks)) + ' tracks.\n')
            else:
                print('    » No possible playlist in this case.\n')

    # save only the longest playlist
    if playlists:
        longest = playlists[0]
        for playlist in playlists[1:]:
            if len(playlist.tracks) > len(longest.tracks):
                longest = playlist

        longest.to_file()

    # show unused tracks
    unused_tracks = set([track for filename, track in meta.tracks.items()]) - set(longest.tracks)
    if unused_tracks:
        print(str(len(unused_tracks)) + ' unused tracks:\n')
        for track in unused_tracks:
            print('    » ' + track.filename)