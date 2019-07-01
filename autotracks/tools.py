#!/usr/bin/env python
# coding: utf-8

import os
import sys

from autotracks import track, playlist, library

class Autotracks():
	def __init__(self, name):
		self.name = name
		self.meta = library.Library()
		self.playlists = []

	def load(self, from_path):
		"""
		Load all audio tracks from a folder or a list of files into the library.
		
		Arguments:
			from_path {str} -- The path to a folder or a list of files.
		"""

		# recursively add all tracks from the given path in the library
		tracks = []
		for item in from_path:
			if os.path.isdir(item):
				for (path, directories, filenames) in os.walk(item):
					# prepend the path to filenames
					tracks.extend(os.path.join(path, filename) for filename in filenames)
					break
			else:
				tracks.append(item)

		if tracks:
			self.meta.add(tracks)

			if len(self.meta.tracks) < 2:
				print('Not enough tracks in list.')
				raise Exception # TODO
		else:
			raise Exception # TODO

	def generate(self):
		"""
		Explore every graph for the track list and generate every playlist
		"""

		for first_filename, first_track in self.meta.tracks.items():
			print('\n⚙   Building and comparing playlists...')
			print('  › Starting with: ' + first_filename + '\n')

			all_last_tracks = [(filename, track) for (filename, track) in self.meta.tracks.items() if filename != first_filename]
			for last_filename, last_track in all_last_tracks:
				print('  › Ending with: ' + last_filename)

				playlist = self.meta.create_playlist(self.name, first_track, last_track)
				if playlist:
					self.playlists.append(playlist)
					print('    » ' + str(len(playlist.tracks)) + ' tracks.\n')
				else:
					print('    » No possible playlist in this case.\n')

	def save_longest_playlist(self):
		"""
		Save the longest generated playlist to a file.
		
		Returns:
			Playlist -- The longest Playlist from all previously generated Playlists.
		"""

		if self.playlists:
			longest = self.playlists[0]
			for playlist in self.playlists[1:]:
				if len(playlist.tracks) > len(longest.tracks):
					longest = playlist

			longest.to_file()

		return longest

	def show_unused_tracks(self, longest):
		"""
		Show the tracks that weren't added to the longest playlist.
		"""

		unused_tracks = set([track for filename, track in self.meta.tracks.items()]) - set(longest.tracks)
		if unused_tracks:
			print(str(len(unused_tracks)) + ' unused tracks:\n')
			for track in unused_tracks:
				print('    » ' + track.filename)