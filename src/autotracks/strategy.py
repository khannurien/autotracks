from abc import ABC, abstractmethod
from typing import List

from src.autotracks.library import Library
from src.autotracks.playlist import Playlist


class Strategy(ABC):
    @abstractmethod
    def generate_playlists(self, library: Library) -> List[Playlist]:
        """
        A strategy should be able to generate multiple playlists from a library of tracks.

        Arguments:
            Library -- The complete library of tracks to consider for playlists generation.

        Returns:
            List[Playlist] -- The set of all possible playlists according to the strategy.
        """

        pass

    @abstractmethod
    def select_playlist(self, playlists: List[Playlist]) -> Playlist:
        """
        A strategy should be able to select one playlist across a set, according to its own criteria.

        Arguments:
            List[Playlist] -- A set of playlists to consider for selection.

        Returns:
            Playlist -- Final playlist selected according to the strategy.
        """

        pass

    @abstractmethod
    def score_playlist(self, playlist: Playlist) -> float:
        """
        A strategy should be able to give a meaningful score to an individual playlist.

        Argument:
            Playlist -- The playlist to score.

        Returns:
            float -- TODO

        """

        pass
