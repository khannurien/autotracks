from typing import List

from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy


class Empty(Strategy):
    def generate_playlists(self, library: Library) -> List[Playlist]:
        """
        TODO

        Returns:
            List[Playlist] -- TODO
        """

        return []

    def select_playlist(self, playlists: List[Playlist]) -> Playlist:
        """
        TODO

        Returns:
            {Playlist} -- TODO
        """

        return Playlist([])

    def score_playlist(self, playlist: Playlist) -> float:
        """
        TODO

        Returns:
            {float} -- TODO
        """
        return 0.0
