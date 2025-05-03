"""Custom URL converter for NutritionalInfo objects.

This module defines a NutritionalInfoConverter that converts URL parameters into
nutritional_info IDs for querying and converts NutritionalInfo objects back into URL-safe strings.
"""

from werkzeug.routing import BaseConverter, ValidationError


class NutritionalInfoConverter(BaseConverter):
    """
    Converter for NutritionalInfo URLs.

    This converter transforms a URL parameter into an integer nutritional_info ID and
    converts a NutritionalInfo object back into a string representation of its nutritional_info_id.
    """

    def __init__(self, map=None):
        """
        Initialize the NutritionalInfoConverter.

        :param map: The URL map provided by the Flask application.
        """
        super().__init__(map)

    def to_python(self, value):
        """
        Convert the URL parameter to an integer nutritional_info ID.

        Flask invokes this method when processing a URL. It attempts to convert the
        provided string value into an integer. If conversion fails, a ValidationError is raised.

        :param value: The string value from the URL.
        :return: The integer nutritional_info ID.
        :raises ValidationError: If the value cannot be converted to an integer.
        """
        try:
            # Convert nutritional_info_id to an integer for querying.
            return int(value)
        except ValueError:
            raise ValidationError(f"Invalid nutritional_info_id: {value}")

    def to_url(self, value):
        """
        Convert a NutritionalInfo object to a URL-safe string.

        This method is invoked when Flask needs to generate a URL. It converts the provided
        NutritionalInfo object's nutritional_info_id attribute into a string.

        :param value: A NutritionalInfo object.
        :return: A string representation of the nutritional_info_id.
        """
        # Convert the NutritionalInfo object back to nutritional_info_id for URL.
        return str(value.nutritional_info_id)
