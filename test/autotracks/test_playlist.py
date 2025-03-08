import pytest

from src.autotracks.autotracks import Autotracks
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.dfs import DFS
from src.autotracks.track import Track


@pytest.fixture
def playlist(datadir: str):
    autotracks = Autotracks([datadir])
    strategy: Strategy = DFS()
    playlists = autotracks.generate_playlists(strategy)
    selected: Playlist = autotracks.select_playlist(strategy, playlists)

    return selected


def test_playlist(datadir: str, playlist: Playlist):
    first_track: Track = playlist.tracks[0]
    for test_track in playlist.tracks[1:]:
        assert test_track.key in first_track.neighbouring_keys()
        first_track = test_track
