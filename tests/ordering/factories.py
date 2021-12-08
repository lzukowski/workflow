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
