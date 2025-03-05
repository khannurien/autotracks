from abc import ABC


class Error(ABC, Exception):
    pass


class MalformedMetaFileError(Error):
    def __init__(self, filename: str, message: str):
        self.filename = filename
        self.message = message


class NotEnoughTracksError(Error):
    def __init__(self, message: str):
        self.message = message
