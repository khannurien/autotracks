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
