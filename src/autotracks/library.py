import logging
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
        self.tracks, self.errors = self.load_metadata(track_filenames)
        self.neighbours = self.find_neighbours(self.tracks)

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

    def load_metadata(
        self, filenames: List[str]
    ) -> Tuple[Dict[str, Track], Dict[str, Error]]:
        """
        TODO

        Arguments:
            filenames {List[str]} -- TODO

        Returns:
            {Tuple[Dict[str, Track], Dict[str, Error]]} -- TODO
        """

        tracks: Dict[str, Track] = {}
        errors: Dict[str, Error] = {}

        # ensure all audio files have associated metadata file
        audio_filenames = [
            filename for filename in filenames if self.is_audio_file(filename)
        ]
        for audio_filename in audio_filenames:
            metadata_filename = f"{audio_filename}.meta"
            # check for cached metadata file
            if not os.path.isfile(metadata_filename):
                # FIXME: handle errors
                self.analyse_audio(audio_filename)

        # read all metadata files and create tracks for the library
        for filename in filenames:
            file_name, file_extension = os.path.splitext(filename)
            if file_extension == ".meta":
                audio_filename = f"{file_name}"
                metadata_filename = f"{file_name}{file_extension}"
                try:
                    bpm, key = self.parse_metadata(metadata_filename)
                    track = Track(audio_filename, metadata_filename, bpm, key)
                    tracks[audio_filename] = track
                except MalformedMetaFileError as error:
                    errors[audio_filename] = error

        return tracks, errors

    def analyse_audio(self, filename: str) -> None:
        """
        Start audio analysis with bpm-tools and keyfinder-cli.
        Metadata will be written to the disk for future use (currently a .meta file next the track's audio file).
        """

        # TODO: use subprocess
        # TODO: remove shell script
        os.system(f'./extract.sh "{filename}"')
        logging.info(f"Analysed audio for file: {filename}")

    def parse_metadata(self, metadata_filename: str) -> Tuple[float, str]:
        """
        Parse metadata file and return BPM and key.

        Arguments:
            metadata_filename {str} -- The filename for the metadata associated with the track.

        Returns:
            Tuple[float, str] -- BPM and key as previously analysed for the track.
        """

        # the .meta file contains two lines -- first is BPM, second is key
        try:
            # TODO: don't read the file one first time, try to parse directly and raise if necessary
            with open(metadata_filename) as meta:
                lines_count = sum(1 for _ in meta)
                if lines_count != 2:
                    raise MalformedMetaFileError(
                        f"Lines in metadata file: {lines_count} (expected 2)",
                    )

            with open(metadata_filename) as meta:
                bpm: float = float(meta.readline().rstrip())
                key: str = meta.readline().rstrip()

                return bpm, key
        except OSError as error:
            raise MalformedMetaFileError(str(error))

    def find_neighbours(
        self, tracks: Dict[str, Track]
    ) -> Dict[str, List[Tuple[float, Track]]]:
        """
        TODO

        Arguments:
            tracks {Dict[str, Track]} -- TODO

        Returns:
            {Dict[str, List[Tuple[float, Track]]]} -- TODO
        """

        neighbours: Dict[str, List[Tuple[float, Track]]] = {}

        for _, track in tracks.items():
            if track.filename not in neighbours:
                neighbours[track.filename] = []
            for _, other in tracks.items():
                if other.filename not in neighbours:
                    neighbours[other.filename] = []
                if other.is_neighbour(track) and other.filename != track.filename:
                    score_for = track.score_for(other)
                    score_from = other.score_for(track)
                    neighbours[track.filename].append((score_for, other))
                    neighbours[other.filename].append((score_from, track))

        return neighbours
