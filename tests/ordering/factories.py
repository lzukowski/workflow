from factory import Factory, Faker, SubFactory
from factory.fuzzy import FuzzyChoice

import ordering
from currency import Currency
from ordering.db.buy_order import DBBuyOrder
from tests.currency.factories import BTCRateFactory


class CreateBuyOrderFactory(Factory):
    class Meta:
        model = ordering.commands.CreateBuyOrder

    id = Faker("uuid4")
    amount = Faker("pydecimal", right_digits=4, min_value=1, max_value=400)
    currency = FuzzyChoice(Currency)


class DBBuyOrderFactory(Factory):
    class Meta:
        model = DBBuyOrder

    request_id = Faker("uuid4")
    paid = Faker("pydecimal", right_digits=4, min_value=1, max_value=400)
    bought = Faker("pydecimal", right_digits=8, min_value=1, max_value=10)
    exchange_rate = SubFactory(BTCRateFactory)
