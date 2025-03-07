from typing import List

from src.autotracks.track import Track


class Playlist:
    tracks: List[Track]

    def __init__(self, tracks: List[Track]) -> None:
        self.tracks = tracks.copy()

    def is_empty(self) -> bool:
        """
        Check if the playlist contains any track.

        Returns:
            {bool} -- True if the playlist is empty.
        """

        return len(self.tracks) == 0
