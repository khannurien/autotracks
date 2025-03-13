from abc import ABC


class Error(ABC, Exception):
    message: str

    pass


class AudioAnalysisError(Error):
    def __init__(self, message: str):
        self.message = message


class MalformedMetaFileError(Error):
    def __init__(self, message: str):
        self.message = message


class NotEnoughTracksError(Error):
    def __init__(self, message: str):
        self.message = message
