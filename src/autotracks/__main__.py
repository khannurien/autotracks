import argparse
import logging
import os
import sys

from datetime import datetime

from src.autotracks.autotracks import Autotracks
from src.autotracks.error import NotEnoughTracksError
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.dfs import DFS


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

    # initialize logger
    if not os.path.exists("log"):
        os.makedirs("log")

    run_time = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    file_handler = logging.FileHandler(f"log/{run_time}.log")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s [%(funcName)18s() ] %(message)s",
        handlers=[file_handler, console_handler],
    )

    # initialize library
    try:
        autotracks = Autotracks(args.filenames)
    except NotEnoughTracksError as error:
        logging.error(error.message)
        sys.exit(2)

    # select strategy
    # TODO: move to program argument
    strategy: Strategy = DFS()

    # generate playlists
    playlists = autotracks.generate_playlists(strategy)

    sorted_playlists = sorted(playlists, key=lambda playlist: len(playlist.tracks))
    print([len(playlist.tracks) for playlist in sorted_playlists])

    # select playlist
    selected: Playlist = autotracks.select_playlist(strategy, playlists)

    # display playlist score
    playlist_score: float = autotracks.score_playlist(strategy, selected)
    logging.info(f"Playlist score: {playlist_score}")

    # write selected playlist to file
    autotracks.write_playlist(selected, args.playlist_name)

    # show library tracks that remain unused in the selected playlist
    autotracks.show_unused_tracks(selected)

    # show errors in library
    autotracks.show_errors()

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
