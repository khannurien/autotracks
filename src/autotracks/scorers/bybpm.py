from src.autotracks.playlist import Playlist
from src.autotracks.scorer import Scorer
from src.autotracks.track import Track


class ByBPM(Scorer):
    """
    Scores track transitions based on BPM similarity.

    Closer BPM values produce lower (better) scores.
    """

    def score_transition(self, from_track: Track, to_track: Track) -> float:
        """
        Score BPM distance between two tracks.

        Arguments:
            from_track {Track} -- The current track.
            to_track {Track} -- The next track.

        Returns:
            float -- BPM distance normalized (lower is better).
        """
        return abs(from_track.metadata.bpm - to_track.metadata.bpm) / 100

    def score_playlist(self, playlist: Playlist) -> float:
        """
        Score a playlist based on its length.

        Arguments:
            playlist {Playlist} -- Playlist to score.

        Returns:
            float -- Total score (higher is better).
        """
        return float(len(playlist.tracks))
