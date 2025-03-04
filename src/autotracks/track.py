from __future__ import annotations

import os
from typing import List, Tuple

from src.autotracks.error import MalformedMetaFileError


class Track:
    bpm: float
    key: str

    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.metadata: str = filename + ".meta"

        # check for cached metadata file
        if not os.path.isfile(self.metadata):
            # FIXME: handle errors
            self.analyse_audio()

        # read metadata
        self.bpm: float
        self.key: str
        self.bpm, self.key = self.get_metadata(self.metadata)

    def analyse_audio(self) -> None:
        """
        Start audio analysis with bpm-tools and keyfinder-cli.
        """

        # TODO: use subprocess
        # TODO: remove shell script
        os.system("./extract.sh '" + self.filename + "'")
        print("Analysed audio for {}".format(self.filename))

    def get_metadata(self, meta_filename: str) -> Tuple[float, str]:
        """
        Parse metadata file and return BPM and key.

        Returns:
            Tuple[float, str] -- BPM, key.
        """

        # the .meta file contains two lines -- first is BPM, second is key
        try:
            # TODO: don't read the file one first time, try to parse directly and raise if necessary
            with open(meta_filename) as meta:
                lines_count = sum(1 for _ in meta)
                if lines_count != 2:
                    raise MalformedMetaFileError(
                        self.filename + ".meta", str(lines_count) + " lines"
                    )

            with open(meta_filename) as meta:
                bpm: float = float(meta.readline().rstrip())
                key: str = meta.readline().rstrip()

                return bpm, key
        except OSError as error:
            print("Could not open file {}.".format(meta_filename))
            raise MalformedMetaFileError(meta_filename, str(error))

    def neighbours(self) -> List[str]:
        """
        Get the list of compatible keys in neighbourhood.

        Returns:
            List[str] -- The list of keys.
        """

        # own key is always a valid neighbour
        neighbourhood = [self.key]

        # find key signature (1-12) and scale (m is Minor, d is Major)
        if 2 <= len(self.key) <= 3:
            if str.isdigit(self.key[1]):
                key_int = int(self.key[0] + self.key[1])
                key_char = self.key[2]
            else:
                key_int = int(self.key[0])
                key_char = self.key[1]
        else:
            raise ValueError("Could not read track key.")

        # cycle through the key wheel (cf. any Harmonic Mixing Wheel)
        if key_int == 12:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append("1" + key_char)

        elif key_int == 1:
            neighbourhood.append("12" + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        else:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        neighbourhood.append(str(key_int) + ("d" if key_char == "m" else "m"))

        return neighbourhood

    def is_neighbour(self, other: Track) -> bool:
        """
        Check if the Track is in the neighbourhood of another Track.

        Arguments:
            other {Track} -- A Track object.

        Returns:
            boolean -- True if both Tracks are neighbours, else False.
        """

        try:
            return self.key in other.neighbours()
        except ValueError:
            return False

    def score_for(self, other: Track) -> float:
        """
        Compute a score for another Track: the closest the BPM, the lower the score.

        Arguments:
            other {Track} -- A Track object.

        Returns:
            float -- The score for the other Track.
        """

        # TODO: check with mod to consider half-time BPM
        # fastest, slowest = min max...
        # div, mod = divmod...

        # if div >= 1:
        #     return...

        return abs(self.bpm - other.bpm) / 100
