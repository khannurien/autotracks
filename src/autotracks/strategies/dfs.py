import math

from typing import Dict, List, Tuple

from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.track import Track


class DFS(Strategy):
    def generate_playlists(self, library: Library) -> List[Playlist]:
        """
        Explore every possible graph for the track list and generate every playlist.

        Returns:
            List[Playlist] -- ...
        """

        playlists: List[Playlist] = []

        for first_filename, first_track in library.tracks.items():
            print("\n⚙   Building and comparing playlists...")
            print(f"  › Starting with: {first_filename}\n")

            all_last_tracks = [
                (filename, track)
                for (filename, track) in library.tracks.items()
                if filename != first_filename
            ]
            for last_filename, last_track in all_last_tracks:
                print(f"  › Ending with: {last_filename}")

                playlist = self.create_playlist(library, first_track, last_track)
                if playlist:
                    playlists.append(playlist)
                    print(f"    » {str(len(playlist.tracks))} tracks.\n")
                else:
                    print("    » No possible playlist in this case.\n")

        return playlists

    def create_playlist(self, library: Library, first: Track, last: Track):
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
        self.discover_graph(library, first, graph)
        paths = self.get_paths(first, last, graph)

        # TODO: why only the longest?
        # get only the longest path
        if paths:
            paths = sorted(paths, key=len, reverse=True)
            path = paths[0]

            # create and return the playlist
            playlist = Playlist()
            for track in path:
                playlist.add(track)

            return playlist
        else:
            return None

    def discover_graph(
        self,
        library: Library,
        first: Track,
        graph: Dict[str, List[Tuple[float, Track]]],
    ):
        """
        Represent the "possible playlists problem" as a graph problem: tracks are nodes
        and edges connect tracks in the same neighbourhood.

        Arguments:
            first {Track} -- A Track object.
            graph {Dict} -- A dictionary which will represent the nodes and edges.
        """

        graph[first.filename] = self.find_successors(library, first)

        for _, next in graph[first.filename]:
            if next.filename not in graph.keys():
                self.discover_graph(library, next, graph)

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

    def find_successors(
        self, library: Library, track: Track
    ) -> List[Tuple[float, Track]]:
        """
        Get the neighbours of a track.

        Arguments:
            track {Track} -- A Track object.

        Returns:
            List[(int, Track)] -- A list of Tracks in the neighbourhood, and their score.
        """

        return library.neighbours[track.filename]

    def select_playlist(self, playlists: List[Playlist]) -> Playlist:
        """
        Naive strategy that selects the longest Playlist across the set.

        Returns:
            Playlist -- The longest Playlist from the list, or an empty Playlist.
        """

        # FIXME: call score_playlist
        # maybe move to abstract class and only implement scoring in concrete class
        if playlists:
            longest: Playlist = playlists[0]
            for playlist in playlists[1:]:
                if len(playlist.tracks) > len(longest.tracks):
                    longest = playlist

            return longest

        return Playlist()

    def score_playlist(self, playlist: Playlist) -> float:
        """
        TODO: compare playlists with a meaningful scoring system

        """
        return -math.inf
