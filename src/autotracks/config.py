import logging
import os
import sys

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from dotenv import dotenv_values


@dataclass
class AutotracksConfig:
    bpm_tag: str
    keyfinder_cli: str


# load environment variables
# environment variables > .env file > default values
default_values = {
    "BPM_TAG": "bpm-tag",
    "KEYFINDER_CLI": "keyfinder-cli",
}
env_values: Dict[str, str | None] = {
    # **default_values,
    **dotenv_values(".env"),
    **{k: os.environ[k] for k in default_values if k in os.environ},
}

# initialize config
config = AutotracksConfig(
    bpm_tag=env_values.get("BPM_TAG") or default_values["BPM_TAG"],
    keyfinder_cli=env_values.get("KEYFINDER_CLI") or default_values["KEYFINDER_CLI"],
)

# initialize logger
if not os.path.exists("log"):
    os.makedirs("log")

run_time = datetime.now().strftime("%Y%m%d-%H%M%S-%f")

file_handler = logging.FileHandler(f"log/{run_time}.log")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)7s [%(funcName)18s] %(message)s",
    handlers=[file_handler, console_handler],
)
