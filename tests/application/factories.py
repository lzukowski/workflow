from factory import DictFactory, Faker
from factory.fuzzy import FuzzyChoice


class ApiCreateBuyOrderRequestFactory(DictFactory):
    request_id = Faker("uuid4")
    amount = Faker("pyfloat", right_digits=4, min_value=1, max_value=400)
    currency = FuzzyChoice(["EUR", "GBP", "USD"])
