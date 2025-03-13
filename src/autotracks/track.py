from __future__ import annotations

from typing import Dict, Tuple


class Track:
    # We use the Open Key Wheel notation: https://gist.github.com/jasonm23/9c7b54c1a00e55ef3bfea187bf4ad7c0#file-open-key-system-harmonic-mixing-md
    # Returned list: Opposite, Before, After
    OPEN_KEY_WHEEL_NEIGHBOURS: Dict[str, Tuple[str, str, str]] = {
        "1m": ("1d", "12m", "2m"),
        "1d": ("1m", "12d", "2d"),
        "2m": ("2d", "1m", "3m"),
        "2d": ("2m", "1d", "3d"),
        "3m": ("3d", "2m", "4m"),
        "3d": ("3m", "2d", "4d"),
        "4m": ("4d", "3m", "5m"),
        "4d": ("4m", "3d", "5d"),
        "5m": ("5d", "4m", "6m"),
        "5d": ("5m", "4d", "6d"),
        "6m": ("6d", "5m", "7m"),
        "6d": ("6m", "5d", "7d"),
        "7m": ("7d", "6m", "8m"),
        "7d": ("7m", "6d", "8d"),
        "8m": ("8d", "7m", "9m"),
        "8d": ("8m", "7d", "9d"),
        "9m": ("9d", "8m", "10m"),
        "9d": ("9m", "8d", "10d"),
        "10m": ("10d", "9m", "11m"),
        "10d": ("10m", "9d", "11d"),
        "11m": ("11d", "10m", "12m"),
        "11d": ("11m", "10d", "12d"),
        "12m": ("12d", "11m", "1m"),
        "12d": ("12m", "11d", "1d"),
    }

    def __init__(
        self, audio_filename: str, metadata_filename: str, bpm: float, key: str
    ) -> None:
        self.filename: str = audio_filename
        self.metadata: str = metadata_filename
        # TODO: add track length
        self.bpm: float = bpm
        self.key: str = key

    def neighbouring_keys(self) -> Tuple[str, str, str]:
        """
        Compatible keys in the track's neighbourhood according to the key wheel.


        Returns:
            List[str] -- The list of compatible keys in neighbourhood of the track.
        """

        return self.OPEN_KEY_WHEEL_NEIGHBOURS[self.key]

    def is_neighbour(self, other: Track) -> bool:
        """
        Check if the track's key is equal to, or is in the neighbourhood of another track's key.

        Arguments:
            other {Track} -- Another track to check key neighbourhood with.

        Returns:
            boolean -- True if both track keys are neighbours, else False.
        """

        return self.key == other.key or self.key in other.neighbouring_keys()

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

        return abs(self.bpm - other.bpm) / 100
