"""
Module for Ingredient API endpoints.

This module defines resources for handling ingredients including retrieving,
creating, updating, and deleting them.
"""

from flask import Response, json, request, jsonify
from flask_restful import Resource
from food_manager.db_operations import (
    create_ingredient,
    get_ingredient_by_id,
    get_all_ingredients,
    update_ingredient,
    delete_ingredient,
)
from food_manager import cache  # Import cache for caching responses
from functools import wraps

def auto_clear_cache(func):
    """Decorator that clears the cache after the wrapped modifying method executes."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # Automatically clear the cache after a modifying operation
        cache.clear()
        return result
    return wrapper

def class_cache(cls):
    """
    Class decorator that applies caching at the class level for GET requests
    and automatically clears the cache after any modifying (POST, PUT, DELETE)
    operation.
    """
    if hasattr(cls, 'get'):
        original_get = cls.get
        @wraps(original_get)
        def cached_get(*args, **kwargs):
            key = request.full_path
            cached_response = cache.get(key)
            if cached_response is not None:
                return cached_response
            response = original_get(*args, **kwargs)
            cache.set(key, response, timeout=86400)
            return response
        cls.get = cached_get

    for method_name in ['post', 'put', 'delete']:
        if hasattr(cls, method_name):
            original_method = getattr(cls, method_name)
            setattr(cls, method_name, auto_clear_cache(original_method))
    return cls

@class_cache
class IngredientListResource(Resource):
    """
    Resource for handling list operations on ingredients (retrieve all, create new).
    """

    def get(self):
        """
        Handle GET requests to retrieve all ingredient items.
        :return: A JSON response containing a list of serialized ingredient objects,
                 or an error message.
        """
        try:
            ingredients = get_all_ingredients()
            return Response(
                json.dumps([ingredient.serialize() for ingredient in ingredients]),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    @classmethod
    def clear_cache(cls):
        """Clears cache for the ingredient list."""
        cache.delete_memoized(cls.get)

    def post(self):
        """
        Handle POST requests to create a new ingredient.
        :return: A JSON response with the serialized newly created ingredient object,
                 or an error message.
        """
        data = request.get_json()
        try:
            ingredient = create_ingredient(**data)
            # Clear cache to reflect new ingredient in list
            self.clear_cache()
            return Response(
                json.dumps(ingredient.serialize()),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

@class_cache
class IngredientResource(Resource):
    """
    Resource for handling operations on a single ingredient (retrieve, update, delete).
    """

    def get(self, ingredient_id):
        """
        Handle GET requests to retrieve a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to retrieve.
        :return: A JSON response with the serialized ingredient object, or an error
                 message if not found.
        """
        ingredient = get_ingredient_by_id(ingredient_id)
        if ingredient:
            return Response(
                json.dumps(ingredient.serialize()),
                200,
                mimetype="application/json"
            )
        else:
            return Response(
                json.dumps({"error": "Ingredient not found"}),
                404,
                mimetype="application/json"
            )

    @classmethod
    def clear_cache(cls, ingredient_id):
        """Clears cache for a specific ingredient and the ingredient list."""
        cache.delete_memoized(cls.get, ingredient_id)
        cache.delete_memoized(IngredientListResource.get)

    def put(self, ingredient_id):
        """
        Handle PUT requests to update an existing ingredient.
        :param ingredient_id: The ID of the ingredient to update.
        :return: A JSON response with the serialized updated ingredient object,
                 or an error message.
        """
        data = request.get_json()
        try:
            ingredient = update_ingredient(ingredient_id, **data)
            # Clear cache for both the specific ingredient and the ingredient list
            self.clear_cache(ingredient_id)
            return Response(
                json.dumps(ingredient.serialize()),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def delete(self, ingredient_id):
        """
        Handle DELETE requests to remove a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is
                 successful, or an error message.
        """
        try:
            delete_ingredient(ingredient_id)
            # Clear cache for both the specific ingredient and the ingredient list
            self.clear_cache(ingredient_id)
            return Response("", 204)
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )
