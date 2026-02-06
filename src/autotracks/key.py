from typing import Dict, Literal, NamedTuple, Tuple, TypeGuard, Union


StandardNotation = Literal[
    "Amin",
    "Emin",
    "Bmin",
    "F#min",
    "C#min",
    "G#min",
    "D#min",
    "A#min",
    "Fmin",
    "Cmin",
    "Gmin",
    "Dmin",
    "Cmaj",
    "Gmaj",
    "Dmaj",
    "Amaj",
    "Emaj",
    "Bmaj",
    "F#maj",
    "C#maj",
    "G#maj",
    "D#maj",
    "A#maj",
    "Fmaj",
]

ShortNotation = Literal[
    "Am",
    "Em",
    "Bm",
    "F#m",
    "C#m",
    "G#m",
    "D#m",
    "A#m",
    "Fm",
    "Cm",
    "Gm",
    "Dm",
    "C",
    "G",
    "D",
    "A",
    "E",
    "B",
    "F#",
    "C#",
    "G#",
    "D#",
    "A#",
    "F",
]

CamelotNotation = Literal[
    "1A",
    "2A",
    "3A",
    "4A",
    "5A",
    "6A",
    "7A",
    "8A",
    "9A",
    "10A",
    "11A",
    "12A",
    "1B",
    "2B",
    "3B",
    "4B",
    "5B",
    "6B",
    "7B",
    "8B",
    "9B",
    "10B",
    "11B",
    "12B",
]

OpenKeyNotation = Literal[
    "1m",
    "2m",
    "3m",
    "4m",
    "5m",
    "6m",
    "7m",
    "8m",
    "9m",
    "10m",
    "11m",
    "12m",
    "1d",
    "2d",
    "3d",
    "4d",
    "5d",
    "6d",
    "7d",
    "8d",
    "9d",
    "10d",
    "11d",
    "12d",
]

KeyNotation = Union[StandardNotation, ShortNotation, CamelotNotation, OpenKeyNotation]


class Key(NamedTuple):
    """
    Represents a musical key with multiple notation systems.

    A Key stores all common representations used in DJ software and music theory,
    along with references to harmonically compatible keys for mixing.

    Attributes:
        standard {StandardNotation} -- Full notation with mode suffix (e.g., "Amin", "Cmaj").
        short {ShortNotation} -- Abbreviated notation (e.g., "Am", "C").
        camelot {CamelotNotation} -- Camelot wheel notation (e.g., "8A", "8B").
        open_key {OpenKeyNotation} -- Open Key notation (e.g., "1m", "1d").
        relative {StandardNotation} -- Relative major/minor key (same Camelot number, different mode).
        previous {StandardNotation} -- Adjacent key counter-clockwise on Camelot wheel (Camelot number - 1).
        next {StandardNotation} -- Adjacent key clockwise on Camelot wheel (Camelot number + 1).
    """

    standard: StandardNotation
    short: ShortNotation
    camelot: CamelotNotation
    open_key: OpenKeyNotation
    relative: StandardNotation
    previous: StandardNotation
    next: StandardNotation

    def __str__(self) -> str:
        """
        Return the standard notation representation of this key.

        Returns:
            str -- The key in standard notation (e.g., "Amin", "Cmaj").
        """
        return self.standard


# All 24 keys with their Camelot wheel mappings.
# Adjacent keys (previous/next) are a perfect fifth apart and mix harmonically.
KEYS: Tuple[Key, ...] = (
    # Minor keys
    Key("Amin", "Am", "8A", "1m", "Cmaj", "Dmin", "Emin"),
    Key("Emin", "Em", "9A", "2m", "Gmaj", "Amin", "Bmin"),
    Key("Bmin", "Bm", "10A", "3m", "Dmaj", "Emin", "F#min"),
    Key("F#min", "F#m", "11A", "4m", "Amaj", "Bmin", "C#min"),
    Key("C#min", "C#m", "12A", "5m", "Emaj", "F#min", "G#min"),
    Key("G#min", "G#m", "1A", "6m", "Bmaj", "C#min", "D#min"),
    Key("D#min", "D#m", "2A", "7m", "F#maj", "G#min", "A#min"),
    Key("A#min", "A#m", "3A", "8m", "C#maj", "D#min", "Fmin"),
    Key("Fmin", "Fm", "4A", "9m", "G#maj", "A#min", "Cmin"),
    Key("Cmin", "Cm", "5A", "10m", "D#maj", "Fmin", "Gmin"),
    Key("Gmin", "Gm", "6A", "11m", "A#maj", "Cmin", "Dmin"),
    Key("Dmin", "Dm", "7A", "12m", "Fmaj", "Gmin", "Amin"),
    # Major keys
    Key("Cmaj", "C", "8B", "1d", "Amin", "Fmaj", "Gmaj"),
    Key("Gmaj", "G", "9B", "2d", "Emin", "Cmaj", "Dmaj"),
    Key("Dmaj", "D", "10B", "3d", "Bmin", "Gmaj", "Amaj"),
    Key("Amaj", "A", "11B", "4d", "F#min", "Dmaj", "Emaj"),
    Key("Emaj", "E", "12B", "5d", "C#min", "Amaj", "Bmaj"),
    Key("Bmaj", "B", "1B", "6d", "G#min", "Emaj", "F#maj"),
    Key("F#maj", "F#", "2B", "7d", "D#min", "Bmaj", "C#maj"),
    Key("C#maj", "C#", "3B", "8d", "A#min", "F#maj", "G#maj"),
    Key("G#maj", "G#", "4B", "9d", "Fmin", "C#maj", "D#maj"),
    Key("D#maj", "D#", "5B", "10d", "Cmin", "G#maj", "A#maj"),
    Key("A#maj", "A#", "6B", "11d", "Gmin", "D#maj", "Fmaj"),
    Key("Fmaj", "F", "7B", "12d", "Dmin", "A#maj", "Cmaj"),
)


# Bidirectional mapping between enharmonic equivalents.
# Used to normalize input so that lookups work regardless of spelling.
ENHARMONIC_EQUIVALENTS: Dict[str, str] = {
    # Flats to sharps
    "Gb": "F#",
    "Db": "C#",
    "Ab": "G#",
    "Eb": "D#",
    "Bb": "A#",
    # Sharps to flats
    "F#": "Gb",
    "C#": "Db",
    "G#": "Ab",
    "D#": "Eb",
    "A#": "Bb",
}


def _normalize(notation: str) -> str:
    """
    Attempt to find an enharmonic equivalent for lookup.

    If the notation doesn't match directly in KEY_LOOKUP, this function
    tries the enharmonic equivalent spelling (e.g., "Gb" <-> "F#").

    Arguments:
        notation {str} -- A key notation string, possibly using alternate spelling.

    Returns:
        str -- The notation with the root converted to its enharmonic equivalent,
               or the original notation if no conversion applies.
    """
    for original, equivalent in ENHARMONIC_EQUIVALENTS.items():
        if notation.startswith(original):
            return notation.replace(original, equivalent, 1)

    return notation


# Lookup table mapping all notation formats to their corresponding Key object.
KEY_LOOKUP: Dict[KeyNotation, Key] = {}

for key in KEYS:
    KEY_LOOKUP[key.standard] = key
    KEY_LOOKUP[key.short] = key
    KEY_LOOKUP[key.camelot] = key
    KEY_LOOKUP[key.open_key] = key


def is_valid_key_notation(notation: str) -> TypeGuard[KeyNotation]:
    """
    Check if a string is a valid key notation.

    Supports standard (Amin, Cmaj), short (Am, C), Camelot (8A, 8B),
    and Open Key (1m, 1d) notations. Also handles enharmonic equivalents
    (e.g., both "Bbmin" and "A#min" are valid).

    Arguments:
        notation {str} -- The string to validate.

    Returns:
        bool -- True if the notation is valid and can be looked up, else False.
    """
    if notation in KEY_LOOKUP:
        return True

    normalized = _normalize(notation)

    return normalized in KEY_LOOKUP


def lookup_key(notation: str) -> Key:
    """
    Look up a Key by any supported notation.

    Accepts standard, short, Camelot, or Open Key notation. Enharmonic
    equivalents are automatically tried if the original notation isn't found.

    Arguments:
        notation {str} -- A key notation string (e.g., "Am", "8A", "Bbmin", "F#m").

    Returns:
        Key -- The Key object corresponding to the notation.

    Raises:
        ValueError -- If the notation is not recognized.
    """
    # Try original notation first
    if notation in KEY_LOOKUP:
        return KEY_LOOKUP[notation]

    # Try enharmonic equivalent
    normalized = _normalize(notation)
    if normalized in KEY_LOOKUP:
        return KEY_LOOKUP[normalized]

    raise ValueError(f"Invalid key notation: {notation}")


def compatible_keys(key: Key) -> Tuple[Key, Key, Key]:
    """
    Get the three harmonically compatible keys for mixing.

    Returns the keys that can be mixed smoothly with the given key:
    - The relative major/minor (same Camelot number, opposite mode)
    - The previous key on the Camelot wheel (counter-clockwise, perfect fourth)
    - The next key on the Camelot wheel (clockwise, perfect fifth)

    Arguments:
        key {Key} -- The key to find compatible keys for.

    Returns:
        Tuple[Key, Key, Key] -- A tuple of (relative, previous, next) Key objects.
    """
    return (
        KEY_LOOKUP[key.relative],
        KEY_LOOKUP[key.previous],
        KEY_LOOKUP[key.next],
    )
