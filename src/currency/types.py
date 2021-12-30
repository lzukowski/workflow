from __future__ import annotations

import decimal
from decimal import Decimal
from enum import Enum


class Currency(str, Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"


def BTC(value: Decimal | float) -> Decimal:
    return Decimal(value).quantize(Decimal(10) ** -8, decimal.ROUND_UP)


def Fiat(value: Decimal | float) -> Decimal:
    return Decimal(value).quantize(Decimal(10) ** -4)
