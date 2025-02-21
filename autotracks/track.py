#/usr/bin/env python
# coding: utf-8

import os

from autotracks.errors import MalformedMetaFileError

class Track():
    def __init__(self, filename):
        self.filename = filename
        self.bpm = None
        self.key = None

        if os.path.isfile(filename + '.meta'):
            self.meta = filename + '.meta'
        else:
            self.meta = None

    def analyse_audio(self):
        """
        Start audio analysis with bpm-tools and keyfinder-cli.
        """

        os.system('./extract.sh "' + self.filename + '"')
        self.meta = self.filename + '.meta'

    def set_meta(self):
        """
        Parse metadata file and save values locally.
        """

        if not self.meta:
            self.analyse_audio()

        # the .meta file contains two lines -- first is key, second is BPM
        try:
            with open(self.meta) as meta:
                lines_count = sum(1 for _ in meta)
                if lines_count != 2:
                    raise MalformedMetaFileError(self.filename + '.meta', str(lines_count) + ' lines')

            with open(self.meta) as meta:
                self.key = meta.readline().rstrip()
                self.bpm = float(meta.readline().rstrip())
        except OSError:
            print('Could not open file {}.'.format(self.filename + '.meta'))

    def neighbours(self):
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
            raise ValueError('Could not read track key.')

        # cycle through the key wheel (cf. any Harmonic Mixing Wheel)
        if key_int == 12:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append('1' + key_char)

        elif key_int == 1:
            neighbourhood.append('12' + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        else:
            neighbourhood.append(str(key_int - 1) + key_char)
            neighbourhood.append(str(key_int + 1) + key_char)

        neighbourhood.append(str(key_int) + ('d' if key_char is 'm' else 'm'))

        return neighbourhood

    def is_neighbour(self, other):
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

    def score_for(self, other):
        """
        Compute a score for another Track: the closest the BPM, the lower the score.

        Arguments:
            other {Track} -- A Track object.

        Returns:
            int -- The score for the other Track.
        """

        return abs(self.bpm - other.bpm) / 100

