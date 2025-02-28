from werkzeug.routing import BaseConverter

class FoodConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert food_id to an integer for querying
        return int(value)

    def to_url(self, value):
        # Convert the Food object back to food_id for URL
        return str(value.food_id)

