"""Custom URL converter for Category objects.

This module defines a CategoryConverter that converts URL parameters to
category IDs (integers) and vice versa. It is used to correctly route URLs
that reference categories.
"""

from werkzeug.routing import BaseConverter, ValidationError


class CategoryConverter(BaseConverter):
    """
    Converter for Category URLs.

    Converts a string from the URL into an integer category ID for database
    queries and converts a Category object back to a URL-safe string.
    """

    def __init__(self, map=None):
        """
        Initialize the CategoryConverter.

        :param map: The URL map passed from the Flask application.
        """
        super().__init__(map)

    def to_python(self, value):
        """
        Convert the URL parameter to an integer category ID.

        Flask calls this method when a URL is matched. It attempts to
        convert the value from the URL into an integer. If conversion fails,
        a ValidationError is raised.

        :param value: The string value from the URL.
        :return: The integer representation of the category ID.
        :raises ValidationError: If the value cannot be converted to an integer.
        """
        try:
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid category_id: {value}")

    def to_url(self, value):
        """
        Convert a Category object to a URL-safe string.

        This method is called when Flask needs to generate a URL. It converts
        the provided Category object's category_id attribute to a string.

        :param value: A Category object.
        :return: A string representation of the category ID.
        """
        return str(value.category_id)
