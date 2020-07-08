#!/usr/bin/env python
# coding: utf-8

import filetype
import os

from autotracks.track import Track
from autotracks.playlist import Playlist
from autotracks.errors import MalformedMetaFileError

class Library():
    def __init__(self):
        self.tracks = {}
        self.neighbours = {}
        self.errors = {}

    def _check_file(self, filename):
        """
        Ensure a file's MIME type is audio/*.

        Arguments:
            filename {str} -- The path to a file.

        Returns:
            boolean -- True if the file is of audio type, else False.
        """

        if os.path.exists(filename):
            fileinfo = filetype.guess(filename)

            if fileinfo:
                if 'audio' in fileinfo.mime:
                    return True

        return False

    def _add(self, track):
        """
        Add a Track to the Library and update its neighbourhood with associated scores.

        Arguments:
            track {Track} -- A Track object.
        """

        self.tracks[track.filename] = track
        self.neighbours[track.filename] = [] 

        for filename, other in self.tracks.items():
            if other.is_neighbour(track) and other.filename != track.filename:
                score_for = track.score_for(other)
                score_from = other.score_for(track)
                self.neighbours[track.filename].append((score_for, other))
                self.neighbours[other.filename].append((score_from, track))

    def count(self):
        """
        Get the number of tracks in the Library.

        Returns:
            int -- The Library's length.
        """

        return len(self.tracks)

    def add(self, filenames):
        """
        Analyse a list of files and add Tracks to the Library.

        Arguments:
            tracks {List[str]} -- The list of filenames to check and add to the Library.
        """

        # create a list of Tracks from filenames according to MIME type
        tracks = [Track(filename) for filename in filenames if self._check_file(filename)]

        total = len(tracks)
        progress = 1

        for track in tracks:
            try:
                print('[{}/{}] Analysing audio for {}'.format(progress, total, track.filename))
                track.set_meta()
                self._add(track)
            except MalformedMetaFileError as error:
                print('✘ Malformed metadata file for {} ({})'.format(error.filename, error.message))
                self.errors[track.filename] = track
            finally:
                progress += 1

    def remove(self, track):
        """
        Remove a Track from the Library and update neighbourhood.

        Arguments:
            track {Track} -- A Track object.
        """

        # remove track from library
        self.tracks.pop(track.filename)
        self.neighbours.pop(track.filename)

        # remove references to it in other tracks' neighbourhood
        updated = dict(self.neighbours)
        for filename, neighbours in self.neighbours.items():
            if track in neighbours:
                updated.pop(track.filename)

        self.neighbours = dict(updated)

    def find_successors(self, track):
        """
        Get the neighbours of a track.

        Arguments:
            track {Track} -- A Track object.

        Returns:
            List[(int, Track)] -- A list of Tracks in the neighbourhood, and their score.
        """

        return self.neighbours[track.filename]

    def discover_graph(self, first, graph):
        """
        Represent the "possible playlists problem" as a graph problem: tracks are nodes
        and edges connect tracks in the same neighbourhood.

        Arguments:
            first {Track} -- A Track object.
            graph {Dict} -- A dictionary which will represent the nodes and edges.
        """

        graph[first.filename] = self.find_successors(first)

        for score, next in graph[first.filename]:
            if next.filename not in graph.keys():
                self.discover_graph(next, graph)

    def get_paths(self, first, last, graph, path=[]):
        """
        Recursive Depth First Search to get all paths from a starting Track to an ending
        Track. Implementation courtesy of https://www.python.org/doc/essays/graphs/ :-)

        Arguments:
            first {Track} -- A Track object.
            last {Track} -- A Track object.
            graph {Dict} -- The representation obtained by self.discover_graph().

        Keyword Arguments:
            path {List[]} -- An empty list to initiate the first path (default: {[]}).

        Returns:
            List[List[Track]] -- The list of paths, represented as lists themselves.
        """

        # each "first" track is added to the path
        path = path + [first]

        # prevent cycles
        if first == last:
            return [path]

        # return an empty list if there is no path to follow
        if not graph.get(first.filename):
            return []

        paths = []
        # float('inf') will always be less than any number
        best_score, best_track = float('inf'), None

        # use successors' score to determine which path to follow
        for score, next in graph[first.filename]:
            if next not in path:
                if score < best_score:
                    best_score, best_track = score, next

        if best_track:
            next_path = self.get_paths(best_track, last, graph, path)

            for new_path in next_path:
                paths.append(new_path)

        return paths

    def create_playlist(self, name, first, last):
        """
        Discover the Library's graph and draw every path betweens tracks.

        Arguments:
            name {str} -- The playlist's name.
            first {Track} -- The starting Track object.
            last {Track} -- The ending Track object.

        Returns:
            Playlist -- The resulting Playlist is the longest path from first to last.
        """

        # discover paths between the first and the last tracks
        graph = {}
        self.discover_graph(first, graph)
        paths = self.get_paths(first, last, graph)

        # get only the longest path
        if paths:
            paths = sorted(paths, key=len, reverse=True)
            path = paths[0]

            # create and return the playlist
            playlist = Playlist(name)
            for track in path:
                playlist.add(track)

            return playlist
        else:
            return None

