from os.path import dirname, join
from typing import Text

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    config: Text = Field(
        join(dirname(__file__), "..", "..", "config.ini"),
        env="CONFIG_FILE",
    )
    coindesk_api_url: Text = Field(
        "https://api.coindesk.com/v1/", env="COINDESK_API_URL",
    )
