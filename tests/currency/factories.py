from factory import Factory, Faker
from factory.fuzzy import FuzzyChoice

from currency import BTCRate, Currency


class BTCRateFactory(Factory):
    class Meta:
        model = BTCRate

    price = Faker(
        "pydecimal", right_digits=4, min_value=36_000, max_value=99_999,
    )
    currency = FuzzyChoice(Currency)
    on_date = Faker("date_time")
