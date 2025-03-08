import os
import pytest

from typing import List, Set

from src.autotracks.autotracks import Autotracks
from src.autotracks.playlist import Playlist
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.empty import Empty
from src.autotracks.track import Track


@pytest.fixture
def autotracks(shared_datadir: str) -> Autotracks:
    return Autotracks([shared_datadir])


@pytest.fixture
def strategy() -> Strategy:
    return Empty()


@pytest.fixture
def selected(autotracks: Autotracks, strategy: Strategy) -> Playlist:
    playlists = autotracks.generate_playlists(strategy)
    return autotracks.select_playlist(strategy, playlists)


@pytest.fixture
def unused(autotracks: Autotracks, selected: Playlist) -> Set[Track]:
    return autotracks.get_unused_tracks(selected)


def test_playlist_length(selected: Playlist):
    assert len(selected.tracks) == 0


def test_playlist_unused(unused: Set[Track]):
    filenames: List[str] = [os.path.basename(track.filename) for track in unused]

    assert len(filenames) == 5
