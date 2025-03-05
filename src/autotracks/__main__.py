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
            "Usage: {autotracks} {playlist} {tracks}".format(
                autotracks=sys.argv[0],
                playlist="<playlist name>",
                tracks="<track list>",
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
    # write selected playlist to file
    autotracks.write_playlist(selected, playlist_name)

    # show unused tracks in the longest playlist
    autotracks.show_unused_tracks(selected)

    # show errors in library
    autotracks.show_errors()

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
