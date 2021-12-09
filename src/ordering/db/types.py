import decimal
from decimal import Decimal

import sqlalchemy as sa


class PreciseNumber(sa.types.TypeDecorator):
    impl = sa.BigInteger
    python_type = Decimal
    cache_ok = True

    def __init__(self, precision, rounding=None) -> None:
        self._multiplier = 10 ** precision
        self._exp = Decimal("1." + "0" * precision)
        self._rounding = rounding
        super().__init__()

    def _quantize(self, value: Decimal) -> Decimal:
        return value.quantize(self._exp, rounding=self._rounding)

    def process_bind_param(self, value, dialect):
        return int(self._quantize(value) * self._multiplier)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        as_decimal = Decimal(value) / self._multiplier
        return self._quantize(as_decimal)


FiatAmountColumn = PreciseNumber(4)
BtcAmountColumn = PreciseNumber(8, decimal.ROUND_UP)
