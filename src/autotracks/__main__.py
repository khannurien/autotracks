import os
import sys
from typing import List

from src.autotracks.autotracks import Autotracks
from src.autotracks.error import NotEnoughTracksError
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.dfs import DFS


def main() -> int:
    # TODO: use argparse instead
    if len(sys.argv) < 3:
        print(
            "Usage: {autotracks} {playlist_name} {filenames}".format(
                autotracks=sys.argv[0],
                playlist_name="<playlist name>",
                filenames="<path to audio tracks folder>",
            )
        )
        sys.exit(1)

    playlist_name: str = sys.argv[1]
    filenames: List[str] = sys.argv[2:]

    # TODO: initialize logger

    # initialize library
    try:
        autotracks = Autotracks(filenames)
    except NotEnoughTracksError as error:
        print(error.message)
        sys.exit(2)

    # select strategy
    # TODO: move to program argument
    strategy: Strategy = DFS()

    # generate playlists
    playlists = autotracks.generate_playlists(strategy)
    # select playlist
    selected: Playlist = autotracks.select_playlist(strategy, playlists)

    # display playlist score
    playlist_score: float = autotracks.score_playlist(strategy, selected)
    print(f"Playlist score: {playlist_score}")

    # write selected playlist to file
    autotracks.write_playlist(selected, playlist_name)

    # show library tracks that remain unused in the selected playlist
    autotracks.show_unused_tracks(selected)

    # show errors in library
    autotracks.show_errors()

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
