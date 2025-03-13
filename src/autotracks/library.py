import logging
import os
import subprocess

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

import magic

from src.autotracks.error import Error, AudioAnalysisError, MalformedMetaFileError
from src.autotracks.track import Track


class Library:
    config: Dict[str, str | None]
    tracks: Dict[str, Track]
    errors: Dict[str, Error]
    neighbours: Dict[str, List[Tuple[float, Track]]]

    def __init__(
        self, config: Dict[str, str | None], track_filenames: List[str]
    ) -> None:
        self.config = config
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
            mime_type: str = magic.from_file(filename, mime=True)

            if mime_type.startswith("audio"):
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

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures: Dict[Future[Tuple[float, str]], str] = {
                executor.submit(self.analyse_audio, audio_filename): audio_filename
                for audio_filename in audio_filenames
                if not os.path.isfile(f"{audio_filename}.meta")
            }

            for future in as_completed(futures):
                audio_filename = futures[future]
                metadata_filename = f"{audio_filename}.meta"
                try:
                    bpm, key = future.result()
                    track = Track(audio_filename, metadata_filename, bpm, key)
                    tracks[audio_filename] = track
                except AudioAnalysisError as error:
                    errors[audio_filename] = error

        # read all metadata files and create tracks for the library
        for filename in filenames:
            file_name, file_extension = os.path.splitext(filename)
            if file_extension == ".meta":
                audio_filename = f"{file_name}"

                if audio_filename not in tracks:
                    metadata_filename = f"{file_name}{file_extension}"
                    try:
                        bpm, key = self.parse_metadata(metadata_filename)
                        track = Track(audio_filename, metadata_filename, bpm, key)
                        tracks[audio_filename] = track
                    except MalformedMetaFileError as error:
                        errors[audio_filename] = error

        return tracks, errors

    def analyse_audio(self, filename: str) -> Tuple[float, str]:
        """
        Start audio analysis with bpm-tag and keyfinder-cli.
        Write metadata to disk for future use in a .meta file next the track's audio file.
        """

        try:
            bpm: float = float(
                subprocess.check_output(
                    f'{self.config["BPM_TAG"]}'
                    f' -nf "{filename}" 2>&1 /dev/null'
                    " | grep \"BPM\" | tail -n 1 | awk -F \": \" '{print $NF}' | cut -d ' ' -f 1",
                    shell=True,
                    text=True,
                ).strip()
            )
            key: str = subprocess.check_output(
                f'{self.config["KEYFINDER_CLI"]} -n openkey "{filename}"',
                shell=True,
                text=True,
            ).strip()

            metadata_filename = f"{filename}.meta"
            with open(metadata_filename, "w") as metadata_file:
                print(bpm, file=metadata_file)
                print(key, file=metadata_file)

            logging.info(
                f"Analysed audio for file: {filename} (got BPM={bpm}; key={key})"
            )

            return bpm, key
        except ValueError as error:
            raise AudioAnalysisError(
                f"Audio analysis error for file: {filename} ({error})"
            )

    def parse_metadata(self, metadata_filename: str) -> Tuple[float, str]:
        """
        Parse metadata file and return BPM and key.

        Arguments:
            metadata_filename {str} -- The filename for the metadata associated with the track.

        Returns:
            Tuple[float, str] -- BPM and key as previously analysed for the track.
        """

        # the .meta file contains two lines -- first is BPM, second is key
        with open(metadata_filename) as meta:
            lines: List[str] = [line.strip() for line in meta.readlines()]

            try:
                bpm: float = float(lines[0])
                key: str = lines[1]

                return bpm, key
            except IndexError as error:
                raise MalformedMetaFileError(
                    f"Lines in metadata file: {len(lines)} (expected 2)",
                )
            except ValueError as error:
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
