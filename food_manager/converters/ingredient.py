from werkzeug.routing import BaseConverter, ValidationError

class IngredientConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert the ingredient_id to an integer for querying
        try:
            return int(value)
        except ValueError:
                raise ValidationError(f"Invalid food_id: {value}")

    def to_url(self, value):
        # Convert the Ingredient object back to ingredient_id for URL
        return str(value.ingredient_id)