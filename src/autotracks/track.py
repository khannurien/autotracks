from __future__ import annotations

from dataclasses import dataclass

from src.autotracks.key import Key, compatible_keys


@dataclass
class TrackMetadata:
    # TODO: add track length
    bpm: float
    key: Key


class Track:
    def __init__(
        self,
        audio_filename: str,
        metadata_filename: str,
        metadata: TrackMetadata,
    ) -> None:
        self.filename: str = audio_filename
        self.metadata_filename: str = metadata_filename
        self.metadata: TrackMetadata = metadata

    def is_neighbour(self, other: Track) -> bool:
        """
        Check if the track's key is equal to, or is in the neighbourhood of another track's key.

        Arguments:
            other {Track} -- Another track to check key neighbourhood with.

        Returns:
            boolean -- True if both track keys are neighbours, else False.
        """

        return (
            self.metadata.key == other.metadata.key
            or other.metadata.key in compatible_keys(self.metadata.key)
        )

    # TODO: Distance score for the key
    # def score_for_key(self, other: Track) -> float:
    #     # count how many steps are needed between the two tracks?

    # TODO: Distance score for the BPM
    # def score_for_bpm(self, other: Track) -> float:

    # TODO: Composite score
    # def score_for(self, other: Track) -> float

    def score_for(self, other: Track) -> float:
        """
        Compute a score for another track: the closer the BPM, the lower the score.

        Arguments:
            other {Track} -- Another track to compare BPM with.

        Returns:
            float -- A distance score (the lower, the better).
        """

        # TODO: check with mod to consider half-time BPM
        # fastest, slowest = min max...
        # div, mod = divmod...

        # if div >= 1:
        #     return...

        # TODO: generally find a better way to score tracks

        return abs(self.metadata.bpm - other.metadata.bpm) / 100
