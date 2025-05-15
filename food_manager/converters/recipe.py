"""
Custom URL converters for the Food Manager application.

This module defines custom converters for recipes, ingredients, and categories.
Each converter transforms URL parameters into corresponding application objects
or identifiers and vice versa.
"""

from werkzeug.routing import BaseConverter, ValidationError

class RecipeConverter(BaseConverter):
    """
    Converter for Recipe objects in URLs.

    This class allows Flask to interpret recipe IDs in URLs and map them to
    corresponding Recipe objects, ensuring that only valid IDs are accepted.
    """



    def to_python(self, value):
        """
        Convert the URL parameter to an integer recipe ID.

        :param value: The string value from the URL.
        :return: The integer recipe ID.
        :raises ValidationError: If the conversion fails.
        """
        try:
            # Convert recipe_id to an integer for querying.
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid recipe_id: {value}")

    def to_url(self, value):
        """
        Convert a Recipe object to a URL-safe string.

        :param value: A Recipe object.
        :return: The string representation of the recipe's ID.
        """
        # Convert the Recipe object back to recipe_id for URL generation.
        return str(value.recipe_id)
