"""
Custom URL converters for the Food Manager application.

This module defines custom converters for recipes, ingredients, and categories.
Each converter transforms URL parameters into corresponding application objects
or identifiers and vice versa.
"""

from werkzeug.routing import BaseConverter, ValidationError
from flask import abort
from food_manager.db_operations import get_recipe_by_id, get_ingredient_by_id, get_category_by_id


class RecipeConverter(BaseConverter):
    """
    Converter for Recipe objects in URLs.

    This class allows Flask to interpret recipe IDs in URLs and map them to
    corresponding Recipe objects, ensuring that only valid IDs are accepted.
    """

    def __init__(self, map=None):
        """
        Initialize the RecipeConverter.

        :param map: The URL map provided by the Flask application.
        """
        super().__init__(map)

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


class IngredientConverter(BaseConverter):
    """
    Converter for Ingredient objects in URLs.

    This class ensures that ingredient IDs in URLs are correctly converted to
    Ingredient objects, returning a 404 error if the ingredient is not found.
    """

    def to_python(self, value):
        """
        Convert the URL parameter to an Ingredient object.

        :param value: The string value from the URL.
        :return: An Ingredient object if found.
        :raises 404 error: If the ingredient is not found.
        """
        # Convert the ingredient_id to an integer and retrieve the Ingredient object.
        ingredient = get_ingredient_by_id(int(value))
        if ingredient is None:
            abort(404, description="Ingredient not found")
        return ingredient

    def to_url(self, value):
        """
        Convert an Ingredient object to a URL-safe string.

        :param value: An Ingredient object.
        :return: The string representation of the ingredient's ID.
        """
        return str(value.ingredient_id)


class CategoryConverter(BaseConverter):
    """
    Converter for Category objects in URLs.

    This class ensures that category IDs in URLs are correctly converted to
    Category objects, returning a 404 error if the category is not found.
    """

    def to_python(self, value):
        """
        Convert the URL parameter to a Category object.

        :param value: The string value from the URL.
        :return: A Category object if found.
        :raises 404 error: If the category is not found.
        """
        # Convert the category_id to an integer and retrieve the Category object.
        category = get_category_by_id(int(value))
        if category is None:
            abort(404, description="Category not found")
        return category

    def to_url(self, value):
        """
        Convert a Category object to a URL-safe string.

        :param value: A Category object.
        :return: The string representation of the category's ID.
        """
        return str(value.category_id)
