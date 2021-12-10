from factory import Factory, Faker
from factory.fuzzy import FuzzyChoice

import ordering
from currency import Currency


class CreateBuyOrderFactory(Factory):
    class Meta:
        model = ordering.commands.CreateBuyOrder

    id = Faker("uuid4")
    amount = Faker("pydecimal", right_digits=4, min_value=1, max_value=400)
    currency = FuzzyChoice(Currency)


class BuyOrderFactory(Factory):
    class Meta:
        model = ordering.queries.BuyOrder

    id = Faker("uuid4")
    request_id = Faker("uuid4")
    bitcoins = Faker("pydecimal", right_digits=8, min_value=0, max_value=99)
    bought_for = Faker("pydecimal", right_digits=4, min_value=1, max_value=9999)
    currency = FuzzyChoice(Currency)
