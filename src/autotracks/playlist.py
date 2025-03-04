from typing import List

from src.autotracks.track import Track


class Playlist:
    tracks: List[Track] = []

    def __init__(self, name: str):
        self.name = name

    def add(self, track: Track) -> None:
        """
        Add a Track to the Playlist.

        Arguments:
            track {Track} -- A Track object.
        """

        if track not in self.tracks:
            self.tracks.append(track)

    def remove(self, track: Track) -> None:
        """
        Remove a Track from the Playlist.

        Arguments:
            track {Track} -- A Track object.
        """

        if track in self.tracks:
            self.tracks.remove(track)

    def to_file(self) -> None:
        """
        Save the Playlist to a playlist_name.m3u file.
        """

        try:
            with open(self.name + ".m3u", mode="w") as playlist:
                for track in self.tracks:
                    playlist.write(
                        "# "
                        + track.key
                        + " @ "
                        + str(round(track.bpm))
                        + "\n"
                        + track.filename
                        + "\n"
                    )
        except OSError:
            print("Could not open file {}.".format(self.name + ".m3u"))
