#!/usr/bin/env python
# coding: utf-8

import os
import sys

class Error(Exception):
    pass

class MalformedMetaFileError(Error):
    def __init__(self, filename, message):
        self.filename = filename
        self.message = message

class NotEnoughTracksError(Error):
    def __init__(self, message):
        self.message = message

