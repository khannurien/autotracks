from abc import ABC, abstractmethod
from typing import List

from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.scorer import Scorer


class Strategy(ABC):
    """
    Abstract base class for building playlists.

    A Strategy determines the relationships between tracks and leverages them to build playlists.
    It must be able to build one or multiple playlists and select the best among them.
    """

    def __init__(self, scorer: Scorer):
        """
        Initialize strategy with a scorer.

        Arguments:
            scorer {Scorer} -- The scorer to use for evaluating tracks.
        """
        self.scorer = scorer

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
