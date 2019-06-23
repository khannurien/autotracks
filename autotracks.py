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

    def analyse_audio(self):
        """Start track analysis with bpm-tools and keyfinder-cli.
        """

        if not self.meta:
            os.system('./extract.sh "' + self.filename + '"')
            self.meta = self.filename + '.meta'

    def set_meta(self):
        """Parse metadata file and save values locally.
        """

        if not self.meta:
            self.analyse_audio()

        with open(self.meta) as meta:
            self.key = meta.readline().rstrip()
            self.bpm = meta.readline().rstrip()

    def neighbours(self):
        """Get the list of compatible keys in neighbourhood.
        """
        
        # own key is always a valid neighbour
        neighbourhood = [self.key]

        # find key signature (1-12) and scale (m is Minor, d is Major)
        if str.isdigit(self.key[1]):
            key_int = int(self.key[0] + self.key[1])
            key_char = self.key[2]
        else:
            key_int = int(self.key[0])
            key_char = self.key[1]

        # cycle through the wheel (cf. any Harmonic Mixing Wheel)
        if key_int == 12:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append('1' + key_char)

        elif key_int == 1:
            neighbourhood.append('12' + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        else:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        neighbourhood.append(str(key_int) + ('d' if key_char is 'm' else 'm'))

        return neighbourhood

    def is_neighbour(self, other):
        return self.key in other.neighbours()

class Playlist():
    def __init__(self, name):
        self.name = name
        self.tracks = []

    def add(self, track):
        """Add a Track to the playlist.
        
        Arguments:
            track {Track} -- A Track object.
        """
        if track not in self.tracks:
            self.tracks.append(track)

    def remove(self, track):
        """Remove a Track from the playlist.
        
        Arguments:
            track {Track} -- A Track object.
        """
        if track in self.tracks:
            self.tracks.remove(track)

    def to_file(self):
        """Save the playlist to an m3u file.
        """
        with open(self.name + '.m3u', mode='w') as playlist:
            for track in self.tracks:
                playlist.write(track.filename + '\n')

class Library():
    def __init__(self):
        self.tracks = {}
        self.keys = set()
        self.neighbours = {}

    def check_file(self, filename):
        """Ensure a file's MIME type is audio/*.
        
        Arguments:
            filename {str} -- The path to a file.
        
        Returns:
            boolean -- True if the file is of audio type, else False.
        """
        fileinfo = filetype.guess(filename)

        if fileinfo:
            if 'audio' in fileinfo.mime:
                return True

        return False

    def add(self, track):
        """Add a Track to the library and update library's neighbourhood.
        
        Arguments:
            track {[type]} -- [description]
        """

        self.tracks[track.filename] = track
        self.keys.add(track.key)
        self.neighbours[track.filename] = set()
        
        for filename, other in self.tracks.items():
            if other.is_neighbour(track) and other.filename != track.filename:
                self.neighbours[track.filename].add(other)
                self.neighbours[other.filename].add(track)

    def add_list(self, filenames):
        """Analyse a list of files and add Tracks to the library.
        
        Arguments:
            tracks {[type]} -- [description]
        """
        for filename in filenames:
            if self.check_file(filename):
                track = Track(filename)
                track.set_meta()
                self.add(track)

    def remove(self, track):
        """Remove a Track from the library and update library's neighbourhood.
        
        Arguments:
            track {Track} -- A Track object.
        """
        self.tracks.pop(track.filename)
        self.neighbours.pop(track.filename)

        for filename, neighbours in self.neighbours.items():
            if track in neighbours:
                neighbours.remove(track)

    def create_playlist(self, name, first, max):
        playlist = Playlist(name)

        i = 0
        while i < max and i < self.count():
            for filename, current in self.tracks.items():
                for track in self.neighbours[filename]:
                    playlist.add(track)
                    i = i + 1

        return playlist

    def count(self):
        return len(self.tracks)

if __name__ == '__main__':
    meta = Library()
    meta.add_list(sys.argv[1:])

    for key, item in meta.tracks.items():
        print(key)
        print(item.key)
        print(item.bpm)
        print(item.neighbours())
        for track in meta.neighbours[item.filename]:
            print('--> ' + track.filename)
        print('\n')
        last = item

    playlist = meta.create_playlist('coucou', last, 2)
    print(playlist.name)
    playlist.to_file()