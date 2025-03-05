import os
from typing import List

from src.autotracks.error import NotEnoughTracksError
from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy


class Autotracks:
    def __init__(self, from_path: List[str]):
        # recursively add all tracks from the given path in the library
        track_filenames: List[str] = []
        for item in from_path:
            if os.path.isdir(item):
                for path, _, filenames in os.walk(item):
                    # prepend the path to filenames
                    track_filenames.extend(
                        os.path.join(path, filename) for filename in filenames
                    )
                    break
            else:
                track_filenames.append(item)

        if track_filenames:
            self.library = Library(track_filenames)

            if len(self.library.tracks) < 2:
                print("Not enough tracks in list.")
                raise NotEnoughTracksError(
                    "Less than two tracks could be added to the library."
                )
        else:
            raise NotEnoughTracksError("No tracks found in list.")

    def show_errors(self) -> None:
        """
        Show the tracks that weren't added to the library because of an error during analysis.
        """

        errors_tracks = len(self.library.errors)
        if errors_tracks > 0:
            print(
                f"\n{str(errors_tracks)} errors happened with the following tracks:\n"
            )
            for filename, _ in self.library.errors.items():
                print("    ✘ {}".format(filename))

    def generate_playlists(self, strategy: Strategy) -> List[Playlist]:
        """
        Apply a given strategy to the library to generate a set of valid playlists.

        Arguments:
            strategy {Strategy} -- A concrete class that implements the strategy inferance.

        Returns:
            List[Playlist] -- A list of valid playlists for the library according to the strategy's criteria.
        """

        return strategy.generate_playlists(self.library)

    def select_playlist(
        self, strategy: Strategy, playlists: List[Playlist]
    ) -> Playlist:
        """
        Apply a given strategy to a set of playlists. This determines the final playlist that Autotracks will return.

        Arguments:
            strategy {Strategy} -- A concrete class that implements the strategy inferance.
            playlists {List[Playlist]} -- A set of previously generated valid playlists.

        Returns:
            Playlist -- A final playlist according to the strategy's criteria.
        """

        return strategy.select_playlist(playlists)

    def write_playlist(self, playlist: Playlist, playlist_filename: str) -> None:
        """
        Save an Autotracks playlist to an m3u file, containing each track's filename and metadata.

        Arguments:
            playlist {Playlist} -- A playlist selected for export.
            playlist_filename {str} -- The finename for the m3u file.
        """

        try:
            with open(playlist_filename, mode="w") as playlist_file:
                for track in playlist.tracks:
                    playlist_file.write(
                        f"# {track.key} @ {str(round(track.bpm))}\n{track.filename}\n"
                    )
        except OSError:
            print("Could not open file {}.".format(playlist_filename))

    def show_unused_tracks(self, playlist: Playlist) -> None:
        """
        Show the tracks that weren't added to a specific playlist.

        Arguments:
            playlist {Playlist} -- An Autotracks playlist to inspect.
        """

        unused_tracks = set([track for _, track in self.library.tracks.items()]) - set(
            playlist.tracks
        )
        if unused_tracks:
            print(f"\n {str(len(unused_tracks))} unused tracks:\n")
            for track in unused_tracks:
                print(
                    "    » "
                    f"{track.filename}"
                    " ("
                    f"{str(track.key)}"
                    " @ "
                    f"{str(round(track.bpm))}"
                    ")"
                )
