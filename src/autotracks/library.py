import os
from typing import Dict, List, Tuple

import filetype  # type: ignore

from src.autotracks.error import Error, MalformedMetaFileError
from src.autotracks.playlist import Playlist
from src.autotracks.track import Track


class Library:
    tracks: Dict[str, Track]
    neighbours: Dict[str, List[Tuple[float, Track]]]
    errors: Dict[str, Error]

    def __init__(self, track_filenames: List[str]) -> None:
        self.tracks, self.neighbours, self.errors = self.load_files(track_filenames)

    def load_files(
        self, filenames: List[str]
    ) -> Tuple[
        Dict[str, Track], Dict[str, List[Tuple[float, Track]]], Dict[str, Error]
    ]:
        """
        Analyse a list of files and add Tracks to the Library.

        Arguments:
            tracks {List[str]} -- The list of filenames to check and add to the Library.

        Returns:
            Tuple[
                Dict[str, Track], Dict[str, List[Tuple[float, Track]]], Dict[str, Error]
            ] --
        """

        audio_filenames = [
            filename for filename in filenames if self.is_audio_file(filename)
        ]

        tracks: Dict[str, Track] = {}
        neighbours: Dict[str, List[Tuple[float, Track]]] = {}
        errors: Dict[str, Error] = {}

        # create all Tracks and initialize their neighbourhoods
        for filename in audio_filenames:
            try:
                track = Track(filename)
                tracks[filename] = track
                neighbours[filename] = []
            except MalformedMetaFileError as error:
                print(
                    "✘ Malformed metadata file for {} ({})".format(
                        error.filename, error.message
                    )
                )
                errors[filename] = error

        # compute all neighbourhoods
        for _, track in tracks.items():
            for _, other in tracks.items():
                if other.is_neighbour(track) and other.filename != track.filename:
                    score_for = track.score_for(other)
                    score_from = other.score_for(track)
                    neighbours[track.filename].append((score_for, other))
                    neighbours[other.filename].append((score_from, track))

        return tracks, neighbours, errors

    def is_audio_file(self, filename: str) -> bool:
        """
        Ensure a file's MIME type is audio/*.

        Arguments:
            filename {str} -- The path to a file.

        Returns:
            boolean -- True if the file is of audio type, else False.
        """

        if os.path.exists(filename):
            fileinfo = filetype.guess(filename)  # type: ignore

            if fileinfo:
                if "audio" in fileinfo.mime:
                    return True

        return False

    def find_successors(self, track: Track) -> List[Tuple[float, Track]]:
        """
        Get the neighbours of a track.

        Arguments:
            track {Track} -- A Track object.

        Returns:
            List[(int, Track)] -- A list of Tracks in the neighbourhood, and their score.
        """

        return self.neighbours[track.filename]

    def discover_graph(self, first: Track, graph: Dict[str, List[Tuple[float, Track]]]):
        """
        Represent the "possible playlists problem" as a graph problem: tracks are nodes
        and edges connect tracks in the same neighbourhood.

        Arguments:
            first {Track} -- A Track object.
            graph {Dict} -- A dictionary which will represent the nodes and edges.
        """

        graph[first.filename] = self.find_successors(first)

        for _, next in graph[first.filename]:
            if next.filename not in graph.keys():
                self.discover_graph(next, graph)

    def get_paths(
        self,
        first: Track,
        last: Track,
        graph: Dict[str, List[Tuple[float, Track]]],
        path: List[Track] = [],
    ) -> List[List[Track]]:
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

        paths: List[List[Track]] = []
        # float('inf') will always be less than any number
        best_score, best_track = float("inf"), None

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

    def create_playlist(self, name: str, first: Track, last: Track):
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
        graph: Dict[str, List[Tuple[float, Track]]] = {}
        # FIXME: make the function tail recursive
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
