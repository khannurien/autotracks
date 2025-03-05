from typing import List

from src.autotracks.track import Track


class Playlist:
    tracks: List[Track] = []

    def add(self, track: Track) -> None:
        """
        Add a track to the playlist.

        Arguments:
            track {Track} -- An Autotracks track object.
        """

        if track not in self.tracks:
            self.tracks.append(track)
