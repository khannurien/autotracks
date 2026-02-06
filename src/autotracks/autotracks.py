import logging
import os

from typing import Dict, List, Set, Tuple

from src.autotracks.error import Error, NotEnoughTracksError
from src.autotracks.library import Library
from src.autotracks.playlist import Playlist
from src.autotracks.scorer import Scorer
from src.autotracks.strategy import Strategy
from src.autotracks.track import Track


class Autotracks:
    library: Library

    def __init__(self, config: Dict[str, str | None], from_path: List[str]):
        # recursively try to add all files from the given path to the library
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

        self.library = Library(config, track_filenames)

    def generate_playlists(self, strategy: Strategy) -> List[Playlist]:
        """
        Apply a given strategy to the library to generate a set of valid playlists.

        Arguments:
            strategy {Strategy} -- A concrete class that implements the strategy inferance.

        Returns:
            List[Playlist] -- A list of valid playlists for the library according to the strategy's criteria.
        """

        if len(self.library.tracks) < 2:
            raise NotEnoughTracksError(
                f"Less than two tracks could be added to the library."
            )

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

    def score_playlist(self, scorer: Scorer, playlist: Playlist) -> float:
        """
        Return the score of a playlist according to a given Scorer.

        Arguments:
            scorer {Scorer} -- The scorer to use for evaluating transitions.
            playlist {Playlist} -- A previously generated valid playlist.
        """
        return scorer.score_playlist(playlist)

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
                    print(
                        f"# {track.metadata.key} @ {round(track.metadata.bpm)}",
                        file=playlist_file,
                    )
                    print(f"{track.filename}", file=playlist_file)
        except OSError:
            logging.error(f"Could not open playlist file: {playlist_filename}")

    def get_unused_tracks(self, playlist: Playlist) -> Set[Track]:
        """
        Lists and returns the tracks that weren't added to a specific playlist.

        Arguments:
            playlist {Playlist} -- An Autotracks playlist to inspect.
        """

        unused_tracks = set([track for _, track in self.library.tracks.items()]) - set(
            playlist.tracks
        )

        return unused_tracks

    def get_errors(self) -> Set[Tuple[str, Error]]:
        """
        Return the errors that happened during audio analysis.

        Returns:
            {Tuple[str, Error]} -- The filename and associated error.
        """

        return set(self.library.errors.items())
