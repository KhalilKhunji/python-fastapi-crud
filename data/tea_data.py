# data/tea_data.py
from models.tea import TeaModel

# We create some instances of our tea model here, which will be used in seeding.
teas_list = [
    TeaModel(name="chai", rating=4, in_stock=True),
    TeaModel(name="earl grey", rating=3, in_stock=False),
    TeaModel(name="matcha", rating=3, in_stock=True),
    TeaModel(name="green tea", rating=5, in_stock=True),
    TeaModel(name="black tea", rating=4, in_stock=True),
    TeaModel(name="oolong", rating=4, in_stock=False),
    TeaModel(name="hibiscus", rating=4, in_stock=True),
    TeaModel(name="peppermint", rating=5, in_stock=True),
    TeaModel(name="jasmine", rating=3, in_stock=True)
]
