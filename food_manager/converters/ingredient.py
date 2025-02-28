from werkzeug.routing import BaseConverter

class IngredientConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert the ingredient_id to an integer for querying
        return int(value)

    def to_url(self, value):
        # Convert the Ingredient object back to ingredient_id for URL
        return str(value.ingredient_id)