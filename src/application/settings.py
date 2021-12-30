from decimal import Decimal
from os.path import dirname, join
from typing import Text

from pydantic import BaseSettings, Field, condecimal


class Settings(BaseSettings):
    config: Text = Field(
        join(dirname(__file__), "..", "..", "config.ini"),
        env="CONFIG_FILE",
    )
    coindesk_api_url: Text = Field(
        "https://api.coindesk.com/v1/", env="COINDESK_API_URL",
    )
    database_url: Text = Field(..., env="DATABASE_URL")
    ordered_btc_limit: condecimal(decimal_places=8) = Field(
        default=Decimal(100), env="ORDERED_BTC_LIMIT",
    )
