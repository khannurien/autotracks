#!/usr/bin/env python
# coding: utf-8

import filetype

from autotracks.track import Track
from autotracks.playlist import Playlist

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

    def discover_graph(self, first, graph):
        graph[first.filename] = self.find_successors(first)

        for next in graph[first.filename]:
            if next.filename not in graph.keys():
                self.discover_graph(next, graph)

    def get_paths(self, first, last, graph, path=[]):
        path = path + [first]

        if first == last:
            return [path]

        if not graph.get(first.filename):
            return []

        paths = []
        for next in graph[first.filename]:
            if next not in path:
                new_paths = self.get_paths(next, last, graph, path)

                for new_path in new_paths:
                    paths.append(new_path)

        return paths

    def create_playlist(self, name, first, last):
        playlist = None

        graph = {}
        self.discover_graph(first, graph)
        paths = self.get_paths(first, last, graph)

        longest = 0

        for path in paths:
            if len(path) > longest:
                del(playlist)
                playlist = Playlist(name)
                for track in path:
                    playlist.add(track)

        return playlist

    def count(self):
        return len(self.tracks)
