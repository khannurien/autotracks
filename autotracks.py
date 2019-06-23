#/usr/bin/env python
# coding: utf-8

import os
import random
import sys

import filetype

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

        # the .meta file contains two lines -- first is key, second is bpm
        with open(self.meta) as meta:
            self.key = meta.readline().rstrip()
            self.bpm = float(meta.readline().rstrip())

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
                playlist.write(
                    track.filename + ' # ' + track.key + ' / ' + str(round(track.bpm)) + '\n'
                )

class Library():
    def __init__(self):
        self.tracks = {}
        self.neighbours = {}

    def _check_file(self, filename):
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

    def _add(self, track):
        """Add a Track to the library and update library's neighbourhood.
        
        Arguments:
            track {Track} -- A Track object.
        """

        self.tracks[track.filename] = track
        self.neighbours[track.filename] = set()
        
        for filename, other in self.tracks.items():
            if other.is_neighbour(track) and other.filename != track.filename:
                self.neighbours[track.filename].add(other)
                self.neighbours[other.filename].add(track)

    def _get_neighbours(self, track):
        """Get the neighbours of a track.
        
        Arguments:
            track {Track} -- A Track object.
        
        Returns:
            List[Track] -- A list of Tracks in the neighbourhood.
        """
        
        return self.neighbours[track.filename]

    def add(self, filenames):
        """Analyse a list of files and add Tracks to the library.
        
        Arguments:
            tracks {[type]} -- [description]
        """
        for filename in filenames:
            if self._check_file(filename):
                track = Track(filename)
                track.set_meta()
                self._add(track)

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

    def find_successors(self, track):
        return self._get_neighbours(track)

    def discover_graph(self, track, graph):
        graph[track.filename] = self.find_successors(track)

        for next in graph[track.filename]:
            if next.filename not in graph.keys():
                self.discover_graph(next, graph)

    def get_paths(self, track):
        graph = {}
        self.discover_graph(track, graph)

        paths = []
        longest = 0
        for filename, neighbours in graph.items():
            path = [track]
            
            # TODO follow the neighbours!
            for next in neighbours:
                if next not in path:
                    path.append(next)
            paths.append(path)

        return paths

    def create_playlist(self, name, first):
        playlist = None
        paths = self.get_paths(first)

        longest = 0
        for path in paths:
            if len(path) > longest:
                playlist = Playlist(name)
                for track in path:
                    playlist.add(track)

        return playlist

    def count(self):
        return len(self.tracks)

if __name__ == '__main__':
    meta = Library()
    meta.add(sys.argv[1:])

    random_filename, random_track = random.choice(list(meta.tracks.items()))
    print("start with: " + random_filename)

    playlist = meta.create_playlist('coucou', random_track)
    playlist.to_file()