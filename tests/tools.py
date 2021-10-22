from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional, Text
from urllib.parse import urljoin

import pytz
import requests_mock


class CoinDeskApiStub:
    CURRENCIES = ["EUR", "GBP", "USD"]

    def __init__(
            self, url: Text, when_last_update: Optional[datetime] = None,
    ) -> None:
        self._url = url
        self._index: Dict[Text, Decimal] = {
            "EUR": Decimal(39_170.1564),
            "GBP": Decimal(33_681.3874),
            "USD": Decimal(46_269.1377),
        }
        self._mark_as_updated(at=when_last_update)

    @contextmanager
    def __call__(self) -> "CoinDeskApiStub":
        with requests_mock.mock(real_http=True) as http:
            http.get(
                urljoin(self._url, "bpi/currentprice.json"),
                json=self._generate_response,
            )
            yield self

    def _generate_response(self, request, context) -> Dict:
        datetime_format = '%b %d, %Y %H:%M:%S %Z'
        utc = pytz.timezone("UTC").localize(self._last_update)
        bst = pytz.timezone("Europe/London").localize(self._last_update)
        return {
            "time": {
                "updated": utc.strftime(datetime_format),
                "updatedISO": self._last_update.isoformat(),
                "updateduk": bst.strftime(datetime_format),
            },
            "disclaimer": (
                "This data was produced from the "
                "CoinDesk Bitcoin Price Index (USD). "
                "Non-USD currency data converted using hourly conversion rate "
                "from openexchangerates.org"
            ),
            "chartName": "Bitcoin",
            "bpi": {
                currency: {
                    "code": currency,
                    "symbol": {
                        "USD": "&#36;",
                        "GBP": "&pound;",
                        "EUR": "&euro;",
                    }[currency],
                    "rate": f"{rate:,.4f}",
                    "description": {
                        "USD": "United States Dollar",
                        "GBP": "British Pound Sterling",
                        "EUR": "Euro",
                    },
                    "rate_float": float(f"{rate:.4f}"),
                }
                for currency, rate in self._index.items()
            },
        }

    def _mark_as_updated(self, at: Optional[datetime] = None) -> None:
        self._last_update = at or datetime.utcnow()

    def get_bitcoin_rate(self, for_currency: CURRENCIES) -> Decimal:
        return self._index[for_currency]

    def set_current(self, rate: Decimal, for_currency: CURRENCIES) -> None:
        self._index[for_currency] = rate
        self._mark_as_updated()
