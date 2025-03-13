import pytest

from typing import Dict


@pytest.fixture(scope="module")
def config() -> Dict[str, str | None]:
    return {
        "BPM_TAG": "bpm-tag",
        "KEYFINDER_CLI": "keyfinder-cli",
    }
