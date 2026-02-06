import os
import pytest

from typing import Dict, List, Set

from src.autotracks.autotracks import Autotracks
from src.autotracks.playlist import Playlist
from src.autotracks.scorer import Scorer
from src.autotracks.scorers.bybpm import ByBPM
from src.autotracks.strategy import Strategy
from src.autotracks.strategies.empty import Empty
from src.autotracks.track import Track


@pytest.fixture
def autotracks(config: Dict[str, str | None], shared_datadir: str) -> Autotracks:
    return Autotracks(config, [shared_datadir])


@pytest.fixture
def scorer() -> Scorer:
    return ByBPM()


@pytest.fixture
def strategy(scorer: Scorer) -> Strategy:
    return Empty(scorer)


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
