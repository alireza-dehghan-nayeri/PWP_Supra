from werkzeug.routing import BaseConverter, ValidationError

class NutritionalInfoConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert nutritional_info_id to an integer for querying
        try:
            return int(value)
        except ValueError:
                raise ValidationError(f"Invalid food_id: {value}")

    def to_url(self, value):
        # Convert the NutritionalInfo object back to nutritional_info_id for URL
        return str(value.nutritional_info_id)
