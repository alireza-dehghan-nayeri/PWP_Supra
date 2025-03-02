"""
Module for Food API endpoints.

This module defines resources for handling food items including
retrieving, creating, updating, and deleting them.
"""

import json
from flask import request, Response
from flask_restful import Resource
from food_manager.db_operations import (
    create_food, get_food_by_id, get_all_foods, update_food, delete_food
)
from food_manager import cache
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
class FoodListResource(Resource):
    """
    Resource for handling operations on the list of food items.
    This includes retrieving all food items (GET) and creating a new food item (POST).
    """

    def get(self):
        """
        Handle GET requests to retrieve all food items.
        :return: A JSON response containing a list of serialized food objects with
                 HTTP status code 200.
        """
        foods = [food.serialize() for food in get_all_foods()]
        return Response(
            json.dumps(foods),
            200,
            mimetype="application/json"
        )

    def post(self):
        """
        Handle POST requests to create a new food item.
        :return: A JSON response with the serialized new food object, or an error
                 message if creation fails.
        """
        data = request.get_json()
        try:
            food = create_food(**data)
            return Response(
                json.dumps(food.serialize()),
                201,
                mimetype="application/json"
            )
        except ValueError as e:
            return Response(
                json.dumps({"error": str(e)}),
                400,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({
                    "error": "An unexpected error occurred.",
                    "details": str(e)
                }),
                500,
                mimetype="application/json"
            )

@class_cache
class FoodResource(Resource):
    """
    Resource for handling operations on a single food item.
    This includes retrieving, updating, and deleting a food item by its unique ID.
    """

    def get(self, food_id):
        """
        Handle GET requests to retrieve a specific food item by its ID.
        :param food_id: The unique identifier of the food item.
        :return: A JSON response with the serialized food object if found, or
                 an error message with HTTP status code 404.
        """
        food = get_food_by_id(food_id)
        if food:
            return Response(
                json.dumps(food.serialize()),
                200,
                mimetype="application/json"
            )
        return Response(
            json.dumps({"error": "Food not found"}),
            404,
            mimetype="application/json"
        )

    def put(self, food_id):
        """
        Handle PUT requests to update an existing food item.
        :param food_id: The unique identifier of the food item to update.
        :return: A JSON response with the serialized updated food object and
                 HTTP status code 200.
        """
        data = request.get_json()
        food = update_food(food_id, **data)
        return Response(
            json.dumps(food.serialize()),
            200,
            mimetype="application/json"
        )

    def delete(self, food_id):
        """
        Handle DELETE requests to remove a specific food item by its ID.
        :param food_id: The unique identifier of the food item to delete.
        :return: A response indicating that the food item was deleted, with
                 HTTP status code 204 (No Content).
        """
        delete_food(food_id)
        return Response(
            "Food Item Deleted",
            204,
            mimetype="application/json"
        )
