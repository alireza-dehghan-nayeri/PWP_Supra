"""Custom URL converter for Food objects.

This module defines a FoodConverter that converts URL parameters to food IDs
(for querying) and converts Food objects back to URL-safe strings.
"""

from werkzeug.routing import BaseConverter, ValidationError


class FoodConverter(BaseConverter):
    """
    Converter for Food URLs.

    This converter transforms a URL parameter into an integer food ID and converts
    a Food object back into a string representation of its food_id.
    """

    def __init__(self, map=None):
        """
        Initialize the FoodConverter.

        :param map: The URL map provided by the Flask application.
        """
        super().__init__(map)

    def to_python(self, value):
        """
        Convert the URL parameter to an integer food ID.

        This method is called by Flask when processing a URL. It attempts to
        convert the given value to an integer. If the conversion fails, a
        ValidationError is raised.

        :param value: The string value from the URL.
        :return: The integer food ID.
        :raises ValidationError: If the value cannot be converted to an integer.
        """
        try:
            # Convert food_id to an integer for querying.
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid food_id: {value}")

    def to_url(self, value):
        """
        Convert a Food object to a URL-safe string.

        This method is called when Flask needs to generate a URL. It converts
        the provided Food object's food_id attribute to a string.

        :param value: A Food object.
        :return: A string representation of the food_id.
        """
        # Convert the Food object back to food_id for URL.
        return str(value.food_id)
