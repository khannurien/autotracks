from abc import ABC, abstractmethod

from src.autotracks.playlist import Playlist
from src.autotracks.track import Track


class Scorer(ABC):
    """
    Abstract base class for scoring track transitions.

    A Scorer determines how well two tracks flow together based on
    their musical properties (BPM, key, energy, etc.).
    """

    @abstractmethod
    def score_transition(self, from_track: Track, to_track: Track) -> float:
        """
        Score the transition from one track to another.

        Arguments:
            from_track {Track} -- The current track.
            to_track {Track} -- The next track.

        Returns:
            float -- Transition distance (lower is better).
        """
        pass

    @abstractmethod
    def score_playlist(self, playlist: Playlist) -> float:
        """
        Score an entire playlist.

        Arguments:
            playlist {Playlist} -- The playlist to score.

        Returns:
            float -- Overall playlist score (higher is better).
        """
        pass
