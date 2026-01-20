import logging
import math

from typing import Dict, List, Optional, Set, Tuple

from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.track import Track


class DFS(Strategy):
    def generate_playlists(self, library: Library) -> List[Playlist]:
        """
        Explore every possible graph for the track list and generate every playlist.

        Arguments:
            library {Library} -- The considered library of tracks.

        Returns:
            List[Playlist] -- A list of all possible playlists that have been discovered
            in the provided library.
        """

        playlists: List[Playlist] = []

        for first_filename, first_track in library.tracks.items():
            logging.debug("⚙ Building and comparing playlists...")
            logging.debug(f"  › Starting with: {first_filename}")

            all_last_tracks = [
                (filename, track)
                for (filename, track) in library.tracks.items()
                if filename != first_filename
            ]
            for last_filename, last_track in all_last_tracks:
                logging.debug(f"    › Ending with: {last_filename}")

                playlist = self.create_playlist(library, first_track, last_track)
                if not playlist.is_empty():
                    playlists.append(playlist)
                    logging.debug(f"      » {len(playlist.tracks)} tracks.")
                else:
                    logging.debug("      » No possible playlist in this case.")

        return playlists

    def create_playlist(self, library: Library, first: Track, last: Track) -> Playlist:
        """
        Discover the library's graph by drawing every path betweens tracks, starting
        from the provided first track. Keep the longest path and save it as a playlist.

        Arguments:
            library {Library} -- The considered library of tracks.
            first {Track} -- A track object that will be the first track in the playlist.
            last {Track} -- A track object that will be the last track in the playlist.

        Returns:
            {Playlist} -- The resulting playlist for the longest path from the provided
            first track to the provided last track.
        """

        # discover all paths between the first and the last tracks
        graph: Dict[str, List[Tuple[float, Track]]] = self.discover_graph(
            library, first
        )

        # create playlists from paths in the graph
        paths: List[List[Track]] = self.get_paths(first, last, graph)
        playlists: List[Playlist] = [Playlist(path_tracks) for path_tracks in paths]

        # only keep the best scoring playlist
        return self.select_playlist(playlists)

    def discover_graph(
        self,
        library: Library,
        first: Track,
        visited: Optional[Set[str]] = None,
    ) -> Dict[str, List[Tuple[float, Track]]]:
        """
        Represent the "possible playlists problem" as a graph problem: tracks are nodes
        and edges connect tracks in the same neighbourhood.

        Arguments:
            library {Library} -- The library containing all tracks and their neighbourhoods.
            first {Track} -- The starting track from which to build the graph.
            visited {Optional[Set[str]]} -- Set of track filenames already visited to
            prevent cycles. Can be None for initial calls.

        Returns:
            {Dict} -- A dictionary representing the graph, where each key is a track filename
            and the value is a list of tuples (score, successor track) representing possible
            next tracks in playlists.
        """

        graph: Dict[str, List[Tuple[float, Track]]] = {}
        graph[first.filename] = self.find_successors(library, first)

        # include current track in the visited set
        history = (visited or set()) | {first.filename}

        for _, next_track in graph[first.filename]:
            if next_track.filename not in history:
                subgraph = self.discover_graph(library, next_track, history)
                graph.update(subgraph)

        return graph

    def get_paths(
        self,
        first_track: Track,
        last_track: Track,
        graph: Dict[str, List[Tuple[float, Track]]],
        path: List[Track] = [],
    ) -> List[List[Track]]:
        """
        Recursive Depth First Search to get all paths from a starting track to an ending track.

        Arguments:
            first {Track} -- A track object that will be the first track in the playlist.
            last {Track} -- A track object that will be the last track in the playlist.
            graph {Dict} -- The representation obtained by self.discover_graph().

        Keyword Arguments:
            path {List[]} -- An empty list to initialize the first path (default: {[]}).

        Returns:
            {List[List[Track]]} -- The list of paths, represented as lists themselves.
        """

        # each "first" track is added to the path
        path = path + [first_track]

        # prevent cycles
        if first_track == last_track:
            return [path]

        # return an empty list if there is no path to follow
        if not graph.get(first_track.filename):
            return []

        paths: List[List[Track]] = []
        # float('inf') will always be more than any number
        best_score, best_track = math.inf, None

        # use successors' score to determine which path to follow
        # the lower the better
        for score, track in graph[first_track.filename]:
            if track not in path:
                if score < best_score:
                    best_score, best_track = score, track

        if best_track:
            next_paths = self.get_paths(best_track, last_track, graph, path)

            for new_path in next_paths:
                paths.append(new_path)

        return paths

    def find_successors(
        self, library: Library, track: Track
    ) -> List[Tuple[float, Track]]:
        """
        Get the neighbours of a track.

        Arguments:
            track {Track} -- A track object.

        Returns:
            {List[(int, Track)]} -- A list of tracks in the neighbourhood, along with their scores.
        """

        # FIXME: allow bigger steps over neighbourhood
        return library.neighbours[track.filename]

    def select_playlist(self, playlists: List[Playlist]) -> Playlist:
        """
        Naive strategy that selects the longest playlist across the set.

        Returns:
            {Playlist} -- The longest playlist from the list, or an empty playlist is the list is empty.
        """

        return next(
            iter(sorted(playlists, key=self.score_playlist, reverse=True)), Playlist([])
        )

    def score_playlist(self, playlist: Playlist) -> float:
        """
        Naive scoring system: the longer the playlist, the higher its score.

        Returns:
            {float} -- The number of tracks in the playlist.
        """
        return float(len(playlist.tracks))
