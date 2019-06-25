#/usr/bin/env python
# coding: utf-8

import os

class Track():
    def __init__(self, filename):
        self.filename = filename

        if os.path.isfile(filename + '.meta'):
            self.meta = filename + '.meta'
        else:
            self.meta = None

    def analyse_audio(self):
        """
        Start track analysis with bpm-tools and keyfinder-cli.
        """

        if not self.meta:
            os.system('./extract.sh "' + self.filename + '"')
            self.meta = self.filename + '.meta'

    def set_meta(self):
        """
        Parse metadata file and save values locally.
        """

        if not self.meta:
            self.analyse_audio()

        # the .meta file contains two lines -- first is key, second is bpm
        try:
            with open(self.meta) as meta:
                self.key = meta.readline().rstrip()
                self.bpm = float(meta.readline().rstrip())
        except OSError:
            print('Could not open file {}.').format(self.name + '.m3u')

    def neighbours(self):
        """
        Get the list of compatible keys in neighbourhood.
        
        Returns:
            List[str] -- The list of keys.
        """
        
        # own key is always a valid neighbour
        neighbourhood = [self.key]

        # find key signature (1-12) and scale (m is Minor, d is Major)
        if str.isdigit(self.key[1]):
            key_int = int(self.key[0] + self.key[1])
            key_char = self.key[2]
        else:
            key_int = int(self.key[0])
            key_char = self.key[1]

        # cycle through the wheel (cf. any Harmonic Mixing Wheel)
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
        Check if the track is in the neighbourhood of another Track.
        
        Arguments:
            other {Track} -- A Track object.
        
        Returns:
            boolean -- True if both tracks are neighbours, else False.
        """
        return self.key in other.neighbours()

    def score_for(self, other):
        """
        [summary]
        
        Arguments:
            other {Track} -- A Track object.
        
        Returns:
            int -- The score for the other Track.
        """

        return abs(self.bpm - other.bpm) / 100