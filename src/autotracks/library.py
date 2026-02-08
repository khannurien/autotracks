from __future__ import annotations

import os
import subprocess

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Callable, Dict, List, Tuple, TypedDict, Union

import magic

from tqdm import tqdm

from src.autotracks.autotracks import AutotracksConfig
from src.autotracks.error import Error, AudioAnalysisError, MalformedMetaFileError
from src.autotracks.key import KeyNotation, is_valid_key_notation, lookup_key
from src.autotracks.track import Track, TrackMetadata


class OldSkoolTrackData(TypedDict):
    bpm: float
    key: KeyNotation


TrackData = Union[OldSkoolTrackData]


class Library:
    """
    A collection of audio tracks with metadata and neighbour relationships.

    Loads tracks from audio files or cached .meta files, analyses new files
    in parallel, and computes harmonic compatibility between tracks.

    Attributes:
        config {Dict[str, str | None]} -- Configuration including paths to analysis tools.
        tracks {Dict[str, Track]} -- Successfully loaded tracks, keyed by audio filename.
        errors {Dict[str, Error]} -- Errors encountered during loading, keyed by filename.
        neighbours {Dict[str, List[Track]]} -- Compatible tracks for each track.
    """

    config: AutotracksConfig
    tracks: Dict[str, Track]
    errors: Dict[str, Error]
    neighbours: Dict[str, List[Track]]

    def __init__(self, config: AutotracksConfig, track_filenames: List[str]) -> None:
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
            mime_type: str = magic.from_file(filename, mime=True)  # type: ignore

            if mime_type.startswith("audio"):
                return True

        return False

    def is_meta_file(self, filename: str) -> bool:
        """
        Weak way to decide if a file is a track metadata file.

        Arguments:
            filename {str} -- The path to a file.

        Returns:
            boolean -- True if the file has a ".meta" extension, else False.
        """
        return filename.endswith(".meta")

    def metadata_filename(self, audio_filename: str) -> str:
        """
        Generate the metadata cache filename for an audio file.

        The metadata filename is the audio filename with a ".meta" extension appended.
        For example, "track.mp3" becomes "track.mp3.meta".

        Arguments:
            audio_filename {str} -- Path to the audio file.

        Returns:
            str -- Path to the corresponding metadata cache file.
        """
        return f"{audio_filename}.meta"

    def audio_filename(self, meta_filename: str) -> str:
        """
        Generate the audio filename for a metadata cache file.

        The audio filename is the metadata filename with the ".meta" extension removed.
        For example, "track.mp3.meta" becomes "track.mp3".

        Arguments:
            meta_filename {str} -- Path to the metadata file.

        Returns:
            str -- Path to the corresponding audio file.
        """
        return meta_filename.removesuffix(".meta")

    def write_metadata(self, track: Track) -> None:
        """
        Write track metadata to a cache file.

        Persists BPM and key information to a .meta file for future use,
        avoiding the need to re-analyse the audio file.

        The file format is plain text with one value per line:
            - Line 1: BPM (float)
            - Line 2: Key (standard notation, e.g., "Amin")

        Arguments:
            track {Track} -- The track whose metadata should be cached.
        """
        with open(track.metadata_filename, "w") as metadata_file:
            print(track.metadata.bpm, file=metadata_file)
            print(track.metadata.key, file=metadata_file)

    def load_metadata(
        self, filenames: List[str]
    ) -> Tuple[Dict[str, Track], Dict[str, Error]]:
        """
        Load or extract metadata for all audio files and return Track objects.

        For files without cached metadata, runs audio analysis in parallel.
        For files with existing .meta files, reads from cache.

        Arguments:
            filenames {List[str]} -- List of audio and/or metadata filenames.

        Returns:
            Tuple[Dict[str, Track], Dict[str, Error]] -- Tracks and errors.
        """
        tracks: Dict[str, Track] = {}
        errors: Dict[str, Error] = {}

        audio_filenames = [f for f in filenames if self.is_audio_file(f)]
        meta_filenames = [f for f in filenames if self.is_meta_file(f)]

        # partition audio files by cached metadata availability
        cached, fresh = self._partition_by_cache(audio_filenames)

        # analyse fresh audio files in parallel
        analysed_tracks, analysed_errors = self._analyse_audio(
            fresh, self._analyse_oldskool
        )
        tracks.update(analysed_tracks)
        errors.update(analysed_errors)

        # load cached metadata files (audio files with associated metadata files)
        cached_meta = [self.metadata_filename(f) for f in cached]
        cached_tracks, cached_errors = self._load_cached(cached_meta)
        tracks.update(cached_tracks)
        errors.update(cached_errors)

        # load orphaned metadata files (passed without corresponding audio file)
        orphaned_meta = self._find_orphan_meta_files(meta_filenames, audio_filenames)
        orphaned_tracks, orphaned_errors = self._load_cached(orphaned_meta)
        tracks.update(orphaned_tracks)
        errors.update(orphaned_errors)

        return tracks, errors

    def _find_orphan_meta_files(
        self, meta_filenames: List[str], audio_filenames: List[str]
    ) -> List[str]:
        """
        Find .meta files whose corresponding audio file wasn't in the input list.

        Arguments:
            meta_filenames {List[str]} -- List of .meta filenames.
            audio_filenames {List[str]} -- List of audio filenames.

        Returns:
            List[str] -- Orphan .meta filenames.
        """
        audio_set = set(audio_filenames)
        orphans: List[str] = []

        for meta_filename in meta_filenames:
            audio_filename = self.audio_filename(meta_filename)
            if audio_filename not in audio_set:
                orphans.append(meta_filename)

        return orphans

    def _partition_by_cache(
        self, audio_filenames: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Partition audio files into cached and fresh.

        Arguments:
            audio_filenames {List[str]} -- List of audio filenames.

        Returns:
            Tuple[List[str], List[str]] -- (cached, fresh) filename lists.
        """
        cached: List[str] = []
        fresh: List[str] = []

        for filename in audio_filenames:
            if os.path.isfile(self.metadata_filename(filename)):
                cached.append(filename)
            else:
                fresh.append(filename)

        return cached, fresh

    def _analyse_audio(
        self,
        audio_filenames: List[str],
        extractor: Callable[[str], TrackData],
    ) -> Tuple[Dict[str, Track], Dict[str, Error]]:
        """
        Analyse audio files without cached metadata in parallel.

        Extracts BPM and key, creates Track objects, and caches metadata.

        Arguments:
            audio_filenames {List[str]} -- Audio files to analyse.
            extractor {Callable[[str], TrackData]} -- Function that takes a filename and returns extracted data.

        Returns:
            Tuple[Dict[str, Track], Dict[str, Error]] -- Tracks and errors.
        """
        tracks: Dict[str, Track] = {}
        errors: Dict[str, Error] = {}

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            futures: Dict[Future[TrackData], str] = {
                executor.submit(extractor, filename): filename
                for filename in audio_filenames
            }

            with tqdm(
                total=len(audio_filenames), desc="Analysing audio files", unit="file"
            ) as pbar:
                for future in as_completed(futures):
                    audio_filename = futures[future]
                    result = self._handle_analysis_result(future, audio_filename)

                    if isinstance(result, Track):
                        tracks[audio_filename] = result
                        self.write_metadata(result)
                    else:
                        errors[audio_filename] = result

                    pbar.update(1)

        return tracks, errors

    def _analyse_oldskool(self, filename: str) -> OldSkoolTrackData:
        """
        Start audio analysis with bpm-tag and keyfinder-cli.

        Arguments:
            filename {str} -- The path to an audio file.

        Returns:
            OldSkoolTrackData -- Dictionary containing BPM (float) and key (KeyNotation).
        """
        try:
            # bpm-tag writes BPM to stderr
            bpm_output: str = subprocess.check_output(
                [self.config.bpm_tag, "-nf", filename],
                stderr=subprocess.STDOUT,
                text=True,
            ).strip()

            # parse bpm-tag output
            bpm_lines = [line for line in bpm_output.splitlines() if "BPM" in line]
            if not bpm_lines:
                raise ValueError(f"No BPM found in output: {bpm_output}")
            last_bpm_line = bpm_lines[-1]
            bpm_str = last_bpm_line.split(": ")[1].split()[0]
            bpm = float(bpm_str)

            key: str = subprocess.check_output(
                [self.config.keyfinder_cli, "-n", "openkey", filename],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()

            if not is_valid_key_notation(key):
                raise ValueError(f"Unknown key notation: {key}")

            return {
                "bpm": bpm,
                "key": key,
            }
        except (IndexError, ValueError, subprocess.CalledProcessError) as error:
            raise AudioAnalysisError(
                f"Audio analysis error for file: {filename} ({error})"
            )

    def _handle_analysis_result(
        self, future: Future[TrackData], audio_filename: str
    ) -> Track | Error:
        """
        Process the result of an audio analysis future.

        Arguments:
            future {Future[TrackData]} -- The completed future.
            audio_filename {str} -- The audio file that was analysed.

        Returns:
            Track | Error -- A Track on success, or an Error on failure.
        """
        try:
            track_data = future.result()
            metadata_filename = self.metadata_filename(audio_filename)
            metadata = TrackMetadata(
                bpm=track_data["bpm"], key=lookup_key(track_data["key"])
            )
            return Track(audio_filename, metadata_filename, metadata)
        except AudioAnalysisError as error:
            return error
        except ValueError as error:
            return AudioAnalysisError(str(error))

    def _load_cached(
        self, meta_filenames: List[str]
    ) -> Tuple[Dict[str, Track], Dict[str, Error]]:
        """
        Load tracks from cached .meta files.

        Arguments:
            meta_filenames {List[str]} -- List of .meta filenames to load.

        Returns:
            Tuple[Dict[str, Track], Dict[str, Error]] -- Tracks and errors, keyed by audio filename.
        """
        tracks: Dict[str, Track] = {}
        errors: Dict[str, Error] = {}

        for meta_filename in meta_filenames:
            audio_filename = self.audio_filename(meta_filename)
            result = self._load_single_cached(audio_filename, meta_filename)

            if isinstance(result, Track):
                tracks[audio_filename] = result
            else:
                errors[audio_filename] = result

        return tracks, errors

    def _load_single_cached(
        self, audio_filename: str, metadata_filename: str
    ) -> Track | Error:
        """
        Load a single track from its cached metadata file.

        Arguments:
            audio_filename {str} -- Path to the audio file.
            metadata_filename {str} -- Path to the .meta file.

        Returns:
            Track | Error -- A Track on success, or an Error on failure.
        """
        try:
            metadata = self.parse_metadata(metadata_filename)
            return Track(audio_filename, metadata_filename, metadata)
        except MalformedMetaFileError as error:
            return error
        except ValueError as error:
            return AudioAnalysisError(str(error))

    def parse_metadata(self, metadata_filename: str) -> TrackMetadata:
        """
        Parse metadata file and return track metadata (including BPM and key).

        Arguments:
            metadata_filename {str} -- The filename for the metadata associated with the track.

        Returns:
            TrackMetadata -- BPM, key and other metadata as previously analysed for the track.
        """

        # the .meta file contains two lines -- first is BPM, second is key
        with open(metadata_filename) as meta:
            lines: List[str] = [line.strip() for line in meta.readlines()]

            try:
                bpm: float = float(lines[0])
                key_str: str = lines[1]
                key = lookup_key(key_str)

                return TrackMetadata(bpm=bpm, key=key)
            except IndexError:
                raise MalformedMetaFileError(
                    f"Lines in metadata file: {len(lines)} (expected 2)",
                )
            except ValueError as error:
                raise MalformedMetaFileError(str(error))

    def find_neighbours(self, tracks: Dict[str, Track]) -> Dict[str, List[Track]]:
        """
        Find harmonically compatible tracks for each track in the library.

        Arguments:
            tracks {Dict[str, Track]} -- All tracks to consider.

        Returns:
            Dict[str, List[Track]] -- For each track filename, a list of harmonically compatible tracks.
        """
        neighbours: Dict[str, List[Track]] = {filename: [] for filename in tracks}

        track_list = list(tracks.values())
        for i, track in enumerate(track_list):
            for other in track_list[i + 1 :]:
                if track.is_neighbour(other):
                    neighbours[track.filename].append(other)
                    neighbours[other.filename].append(track)

        return neighbours
