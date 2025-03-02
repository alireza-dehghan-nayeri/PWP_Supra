"""
Module for Nutritional Information API endpoints.

This module defines resources for handling nutritional information items.
It supports GET (list and detail), POST, PUT, and DELETE operations.
"""

from flask import Response, json, request
from flask_restful import Resource
from food_manager.db_operations import (
    create_nutritional_info, get_all_nutritions, get_nutritional_info_by_id,
    update_nutritional_info, delete_nutritional_info
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
class NutritionalInfoListResource(Resource):
    """
    Resource for handling operations on the list of nutritional information items.
    This includes retrieving all nutritional info items (GET) and creating a new 
    nutritional info item (POST).
    """

    def get(self):
        """
        Handle GET requests to retrieve all nutritional information items.
        :return: A JSON response containing a list of serialized nutritional info
                 objects with HTTP status code 200.
        """
        try:
            nutritional_infos = get_all_nutritions()
            return Response(
                json.dumps(
                    [nutritional_info.serialize() for nutritional_info in nutritional_infos]
                ),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def post(self):
        """
        Handle POST requests to create a new nutritional information item.
        :return: A JSON response with the serialized new nutritional info object or 
                 an error message if creation fails.
        """
        data = request.get_json()
        try:
            nutritional_info = create_nutritional_info(**data)
            return Response(
                json.dumps(nutritional_info.serialize()),
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
class NutritionalInfoResource(Resource):
    """
    Resource for handling operations on a single nutritional information item.
    This includes retrieving, updating, and deleting a nutritional info item by its ID.
    """

    def get(self, nutritional_info_id):
        """
        Handle GET requests to retrieve a specific nutritional info item by its ID.
        :param nutritional_info_id: The unique identifier of the nutritional info item.
        :return: A JSON response with the serialized nutritional info object if found,
                 or an error message with HTTP status code 404 if not found.
        """
        try:
            nutritional_info = get_nutritional_info_by_id(nutritional_info_id)
            if nutritional_info:
                return Response(
                    json.dumps(nutritional_info.serialize()),
                    200,
                    mimetype="application/json"
                )
            return Response(
                json.dumps({"error": "Nutritional Info not found"}),
                404,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def put(self, nutritional_info_id):
        """
        Handle PUT requests to update an existing nutritional info item.
        :param nutritional_info_id: The unique identifier of the nutritional info item to update.
        :return: A JSON response with the serialized updated nutritional info object,
                 or an error message if the update fails.
        """
        data = request.get_json()
        try:
            nutritional_info = update_nutritional_info(nutritional_info_id, **data)
            return Response(
                json.dumps(nutritional_info.serialize()),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def delete(self, nutritional_info_id):
        """
        Handle DELETE requests to remove a specific nutritional info item by its ID.
        :param nutritional_info_id: The unique identifier of the nutritional info item to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is successful,
                 or an error message if deletion fails.
        """
        try:
            delete_nutritional_info(nutritional_info_id)
            return Response("", 204)
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )
