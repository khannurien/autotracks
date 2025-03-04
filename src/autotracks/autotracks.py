import os
from typing import List

from src.autotracks.error import NotEnoughTracksError
from src.autotracks.library import Library
from src.autotracks.playlist import Playlist


class Autotracks:
    def __init__(self, playlist_name: str, from_path: List[str]):
        self.playlist_name = playlist_name

        # recursively add all tracks from the given path in the library
        track_filenames: List[str] = []
        for item in from_path:
            if os.path.isdir(item):
                for path, _, filenames in os.walk(item):
                    # prepend the path to filenames
                    track_filenames.extend(
                        os.path.join(path, filename) for filename in filenames
                    )
                    break
            else:
                track_filenames.append(item)

        if track_filenames:
            self.library = Library(track_filenames)

            if len(self.library.tracks) < 2:
                print("Not enough tracks in list.")
                raise NotEnoughTracksError(
                    "Less than two tracks could be added to the library."
                )
        else:
            raise NotEnoughTracksError("No tracks found in list.")

    def generate_playlists(self) -> List[Playlist]:
        """
        Explore every possible graph for the track list and generate every playlist.
        """

        playlists: List[Playlist] = []

        for first_filename, first_track in self.library.tracks.items():
            print("\n⚙   Building and comparing playlists...")
            print("  › Starting with: " + first_filename + "\n")

            all_last_tracks = [
                (filename, track)
                for (filename, track) in self.library.tracks.items()
                if filename != first_filename
            ]
            for last_filename, last_track in all_last_tracks:
                print("  › Ending with: " + last_filename)

                playlist = self.library.create_playlist(
                    self.playlist_name, first_track, last_track
                )
                if playlist:
                    playlists.append(playlist)
                    print("    » " + str(len(playlist.tracks)) + " tracks.\n")
                else:
                    print("    » No possible playlist in this case.\n")

        return playlists

    def get_longest_playlist(self, playlists: List[Playlist]) -> Playlist:
        """
        Return the longest Playlist in the list.

        Returns:
            Playlist -- The longest Playlist from a list of previously generated Playlists.
        """

        if playlists:
            longest: Playlist = playlists[0]
            for playlist in playlists[1:]:
                if len(playlist.tracks) > len(longest.tracks):
                    longest = playlist

            return longest

        return Playlist(self.playlist_name)

    def show_unused_tracks(self, longest: Playlist) -> None:
        """
        Show the tracks that weren't added to the longest playlist.
        """

        unused_tracks = set([track for _, track in self.library.tracks.items()]) - set(
            longest.tracks
        )
        if unused_tracks:
            print("\n" + str(len(unused_tracks)) + " unused tracks:\n")
            for track in unused_tracks:
                print(
                    "    » "
                    + track.filename
                    + " ("
                    + str(track.key)
                    + " @ "
                    + str(round(track.bpm))
                    + ")"
                )

    def show_errors(self) -> None:
        """
        Show the tracks that weren't added to the playlist because of an error during analysis.
        """

        errors_tracks = len(self.library.errors)
        if errors_tracks > 0:
            print(
                "\n"
                + str(errors_tracks)
                + " errors happened with the following tracks:\n"
            )
            for filename, _ in self.library.errors.items():
                print("    ✘ {}".format(filename))
