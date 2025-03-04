import os
import sys
from typing import List

from src.autotracks.autotracks import Autotracks
from src.autotracks.error import NotEnoughTracksError
from src.autotracks.playlist import Playlist


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

    # initialize library
    try:
        autotracks = Autotracks(playlist_name, filenames)
    except NotEnoughTracksError as error:
        print(error.message)
        sys.exit(2)

    # generate playlists and save the longest
    # TODO: we should score each playlist instead (according to what metric?)
    playlists = autotracks.generate_playlists()
    longest: Playlist = autotracks.get_longest_playlist(playlists)
    longest.to_file()

    # show unused tracks in the longest playlist
    autotracks.show_unused_tracks(longest)

    # show errors in library
    autotracks.show_errors()

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
