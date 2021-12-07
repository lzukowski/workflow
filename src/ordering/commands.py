from pydantic import condecimal

from application.bus import Command
from currency import Currency


class CreateBuyOrder(Command):
    amount: condecimal(decimal_places=4)
    currency: Currency
