"""
Module for Ingredient API endpoints.

This module defines resources for handling ingredients including retrieving,
creating, updating, and deleting them.
"""

from flask import request
from flask_restful import Resource

from food_manager.db_operations import (
    create_ingredient,
    get_ingredient_by_id,
    get_all_ingredients,
    update_ingredient,
    delete_ingredient,
)
from food_manager.utils.reponses import ResourceMixin
from food_manager import cache  # Import cache for caching responses


# Define resource for handling list operations on ingredients (retrieve all, create new)
class IngredientListResource(Resource, ResourceMixin):
    @cache.cached(timeout=86400)  # Cache the GET result for 24 hours (86400 sec)
    def get(self):
        """
        Handle GET requests to retrieve all ingredient items.
        :return: A JSON response containing a list of serialized ingredient objects,
                 or an error message.
        """
        return self.handle_get_all(get_all_ingredients)

    def post(self):
        """
        Handle POST requests to create a new ingredient.
        :return: A JSON response with the serialized newly created ingredient object,
                 or an error message.
        """
        return self.handle_create(create_ingredient, request.get_json())


# Define resource for handling operations on a single ingredient (retrieve, update, delete)
class IngredientResource(Resource, ResourceMixin):
    @cache.cached(timeout=86400)  # Cache the GET result for 24 hours (86400 sec)
    def get(self, ingredient_id):
        """
        Handle GET requests to retrieve a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to retrieve.
        :return: A JSON response with the serialized ingredient object, or an error
                 message if not found.
        """
        return self.handle_get_by_id(get_ingredient_by_id, ingredient_id)

    def put(self, ingredient_id):
        """
        Handle PUT requests to update an existing ingredient.
        :param ingredient_id: The ID of the ingredient to update.
        :return: A JSON response with the serialized updated ingredient object,
                 or an error message.
        """
        return self.handle_update(update_ingredient, ingredient_id)

    def delete(self, ingredient_id):
        """
        Handle DELETE requests to remove a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is
                 successful, or an error message.
        """
        return self.handle_delete(delete_ingredient, ingredient_id)
