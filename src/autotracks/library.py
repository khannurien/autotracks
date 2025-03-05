import os
from typing import Dict, List, Tuple

import filetype  # type: ignore

from src.autotracks.error import Error, MalformedMetaFileError
from src.autotracks.track import Track


class Library:
    tracks: Dict[str, Track]
    neighbours: Dict[str, List[Tuple[float, Track]]]
    errors: Dict[str, Error]

    def __init__(self, track_filenames: List[str]) -> None:
        self.tracks, self.neighbours, self.errors = self.load_files(track_filenames)

    def load_files(
        self, filenames: List[str]
    ) -> Tuple[
        Dict[str, Track], Dict[str, List[Tuple[float, Track]]], Dict[str, Error]
    ]:
        """
        Analyse a list of files and add audio tracks to the library.

        Arguments:
            filenames {List[str]} -- The list of filenames to check for addition to the library.

        Returns:
            Tuple[Dict[str, Track], Dict[str, List[Tuple[float, Track]]], Dict[str, Error]] -- TODO: improve file structures and docs
        """

        audio_filenames = [
            filename for filename in filenames if self.is_audio_file(filename)
        ]

        tracks: Dict[str, Track] = {}
        neighbours: Dict[str, List[Tuple[float, Track]]] = {}
        errors: Dict[str, Error] = {}

        # create all Tracks and initialize their neighbourhoods
        for filename in audio_filenames:
            try:
                track = Track(filename)
                tracks[filename] = track
                neighbours[filename] = []
            except MalformedMetaFileError as error:
                print(
                    "✘ Malformed metadata file for {} ({})".format(
                        error.filename, error.message
                    )
                )
                errors[filename] = error

        # compute all neighbourhoods
        for _, track in tracks.items():
            for _, other in tracks.items():
                if other.is_neighbour(track) and other.filename != track.filename:
                    score_for = track.score_for(other)
                    score_from = other.score_for(track)
                    neighbours[track.filename].append((score_for, other))
                    neighbours[other.filename].append((score_from, track))

        return tracks, neighbours, errors

    def is_audio_file(self, filename: str) -> bool:
        """
        Ensure a file's MIME type is audio/*.

        Arguments:
            filename {str} -- The path to a file.

        Returns:
            boolean -- True if the file is of audio type, else False.
        """

        if os.path.exists(filename):
            fileinfo = filetype.guess(filename)  # type: ignore

            if fileinfo:
                if "audio" in fileinfo.mime:  # type: ignore
                    return True

        return False
