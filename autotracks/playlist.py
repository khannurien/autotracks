#!/usr/bin/env python
# coding: utf-8

from autotracks.track import Track

class Playlist():
    def __init__(self, name):
        self.name = name
        self.tracks = []

    def add(self, track):
        """
        Add a Track to the playlist.
        
        Arguments:
            track {Track} -- A Track object.
        """

        if track not in self.tracks:
            self.tracks.append(track)

    def remove(self, track):
        """
        Remove a Track from the playlist.
        
        Arguments:
            track {Track} -- A Track object.
        """
  
        if track in self.tracks:
            self.tracks.remove(track)

    def to_file(self):
        """
        Save the playlist to an m3u file.
        """
  
        try:
            with open(self.name + '.m3u', mode='w') as playlist:
                for track in self.tracks:
                    playlist.write(
                        '# ' + track.key + ' @ ' + str(round(track.bpm)) + '\n'
                        + track.filename + '\n'
                    )
        except OSError:
            print('Could not open file {}.').format(self.name + '.m3u')
