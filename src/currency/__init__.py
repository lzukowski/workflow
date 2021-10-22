from enum import Enum


class Currency(str, Enum):
    GBP = "GBP"
    EUR = "EUR"
    USD = "USD"


__all__ = ["Currency"]
