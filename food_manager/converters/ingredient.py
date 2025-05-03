"""Custom URL converter for Ingredient objects.

This module defines an IngredientConverter that converts URL parameters into
ingredient IDs for querying and converts Ingredient objects back into URL-safe strings.
"""

from werkzeug.routing import BaseConverter, ValidationError


class IngredientConverter(BaseConverter):
    """
    Converter for Ingredient URLs.

    This converter transforms a URL parameter into an integer ingredient ID and
    converts an Ingredient object back into a string representation of its ingredient_id.
    """

    def __init__(self, map=None):
        """
        Initialize the IngredientConverter.

        :param map: The URL map provided by the Flask application.
        """
        super().__init__(map)

    def to_python(self, value):
        """
        Convert the URL parameter to an integer ingredient ID.

        Flask calls this method when processing a URL. It attempts to convert
        the given value to an integer. If the conversion fails, a ValidationError is raised.

        :param value: The string value from the URL.
        :return: The integer ingredient ID.
        :raises ValidationError: If the value cannot be converted to an integer.
        """
        try:
            # Convert the ingredient_id to an integer for querying.
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid ingredient_id: {value}")

    def to_url(self, value):
        """
        Convert an Ingredient object to a URL-safe string.

        This method is called when Flask needs to generate a URL. It converts the provided
        Ingredient object's ingredient_id attribute to a string.

        :param value: An Ingredient object.
        :return: A string representation of the ingredient_id.
        """
        # Convert the Ingredient object back to ingredient_id for URL.
        return str(value.ingredient_id)
