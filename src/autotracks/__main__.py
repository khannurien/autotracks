import argparse
import logging
import os
import sys
import time

from typing import Set, Tuple

from src.autotracks.autotracks import Autotracks
from src.autotracks.error import Error, NotEnoughTracksError
from src.autotracks.playlist import Playlist
from src.autotracks.scorer import Scorer
from src.autotracks.scorers.bybpm import ByBPM
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.dfs import DFS
from src.autotracks.track import Track

from src.autotracks.config import config


def main() -> int:
    # initialize argument parser
    parser = argparse.ArgumentParser(
        description=(
            "🎶 Generate automatic playlists according to your tracks' mood and groove"
        )
    )

    parser.add_argument(
        "playlist_name",
        help="The filename for the resulting playlist, including extension",
    )

    parser.add_argument(
        "filenames", nargs="+", help="A list of paths to explore for audio tracks"
    )

    args = parser.parse_args()

    # initialize library
    autotracks = Autotracks(config, args.filenames)

    try:
        # select scorer
        # TODO: move to program argument
        scorer: Scorer = ByBPM()

        # select strategy
        # TODO: move to program argument
        strategy: Strategy = DFS(scorer)

        # generate playlists and measure elapsed time
        start: float = time.perf_counter()
        playlists = autotracks.generate_playlists(strategy)
        end: float = time.perf_counter()
        elapsed = end - start
        logging.info(f"Elapsed time (seconds): {elapsed}")

        # select playlist
        selected: Playlist = autotracks.select_playlist(strategy, playlists)

        # display playlist score
        playlist_score: float = autotracks.score_playlist(scorer, selected)
        logging.info(f"Playlist score: {playlist_score}")

        # write selected playlist to file
        autotracks.write_playlist(selected, args.playlist_name)

        # show library tracks that remain unused in the selected playlist
        unused: Set[Track] = autotracks.get_unused_tracks(selected)
        for track in unused:
            logging.warning(
                f"⚠ Unused track: {track.filename} ({track.metadata.key} @ {round(track.metadata.bpm)})"
            )
    except NotEnoughTracksError as error:
        # can't work with that
        logging.error(error.message)
        return os.EX_DATAERR
    finally:
        # show files that produced errors during analysis
        errors: Set[Tuple[str, Error]] = autotracks.get_errors()
        for filename, error in errors:
            logging.error(f"✘ Error with file: {filename} ({error.message})")

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
