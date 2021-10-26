from os.path import dirname, join
from typing import Text

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    config: Text = Field(
        join(dirname(__file__), "..", "..", "config.ini"),
        env="CONFIG_FILE",
    )
