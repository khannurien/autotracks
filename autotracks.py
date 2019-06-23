#/usr/bin/env python
# coding: utf-8

import os
import sys

import filetype
from filetype.types.audio import Flac

class Track():
    def __init__(self, filename):
        self.filename = filename

        if os.path.isfile(filename + '.meta'):
            self.meta = filename + '.meta'
        else:
            self.meta = None

    def analyse_track(self):
        """Start track analysis with bpm-tools and keyfinder-cli.
        """

        if not self.meta:
            os.system('./extract.sh "' + self.filename + '"')
            self.meta = self.filename + '.meta'

    def get_meta(self):
        """Parse metadata file and save values locally.
        """

        if not self.meta:
            self.analyse_track()

        with open(self.meta) as meta:
            self.key = meta.readline().rstrip()
            self.bpm = meta.readline().rstrip()

    def neighbours(self):
        """Get the list of compatible keys in neighbourhood.
        """
        def opposite(char):
            if char == 'd':
                return 'm'
            else:
                return 'd'

        neighbourhood = []

        if str.isdigit(self.key[1]):
            key_int = int(self.key[0] + self.key[1])
            key_char = self.key[2]
        else:
            key_int = int(self.key[0])
            key_char = self.key[1]

        if key_int == 12:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append('1' + key_char)
            
        elif key_int == 1:
            neighbourhood.append('12' + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        else:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        neighbourhood.append(str(key_int) + opposite(key_char))

        return neighbourhood

    def is_neighbour(self, other):
        return self.key in other.neighbours()

class Playlist():
    def __init__(self, name):
        self.name = name
        self.tracks = []

    def add(self, track):
        if track not in self.tracks:
            self.tracks.append(track)

    def remove(self, track):
        if track in self.tracks:
            self.tracks.remove(track)

    def to_file(self):
        with open(self.name + '.m3u', mode='w') as playlist:
            for track in self.tracks:
                playlist.write(track.filename + '\n')

class Library():
    def __init__(self):
        self.tracks = {}
        self.keys = set()
        self.neighbours = {}

    def add(self, track):
        self.tracks[track.filename] = track
        self.keys.add(track.key)
        self.neighbours[track.filename] = set()
        
        neighbourhood = track.neighbours()
        for filename, other in self.tracks.items():
            if other.key in neighbourhood:
                self.neighbours[track.filename].add(other)
                self.neighbours[other.filename].add(track)

    def remove(self, track):
        self.tracks.pop(track.filename)
        self.neighbours.pop(track.filename)

        for filename, neighbours in self.neighbours.items():
            if track in neighbours:
                neighbours.remove(track)

    def count(self):
        return len(self.tracks)

if __name__ == '__main__':
    meta = Library()
    playlist = Playlist('zbeul')

    for filename in sys.argv[1:]:
        fileinfo = filetype.guess(filename)

        if fileinfo:
            if 'audio' in fileinfo.mime:
                track = Track(filename)
                track.analyse_track()
                track.get_meta()
                meta.add(track)
                playlist.add(track)

    playlist.to_file()

    for key, item in meta.tracks.items():
        print(key)
        print(item.filename)
        print(item.meta)
        print(item.key)
        print(item.bpm)
        print(item.neighbours())
        for track in meta.neighbours[item.filename]:
            print(track.filename)