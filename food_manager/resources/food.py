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


# Food Resources

class FoodListResource(Resource):
    """
    Resource for handling operations on the list of food items.
    This includes retrieving all food items (GET) and creating a new food item (POST).
    """

    @cache.cached(timeout=86400)  # Cache GET request for 24 hours (86400 seconds)
    def get(self):
        """
        Handle GET requests to retrieve all food items.
        :return: A JSON response containing a list of serialized food objects with
                 HTTP status code 200.
        """
        # Retrieve all food objects from the database and serialize each object
        foods = [food.serialize() for food in get_all_foods()]
        # Return the list of serialized food objects as JSON with status 200
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
        # Extract JSON payload from the incoming request
        data = request.get_json()
        try:
            # Create a new food item using the provided data
            food = create_food(**data)
            # Serialize and return the new food object with HTTP status 201 (Created)
            return Response(
                json.dumps(food.serialize()),
                201,
                mimetype="application/json"
            )
        except ValueError as e:
            # Return a JSON error response with HTTP status 400 (Bad Request)
            return Response(
                json.dumps({"error": str(e)}),
                400,
                mimetype="application/json"
            )
        except Exception as e:
            # Return a JSON error response with HTTP status 500 (Internal Server Error)
            return Response(
                json.dumps({
                    "error": "An unexpected error occurred.",
                    "details": str(e)
                }),
                500,
                mimetype="application/json"
            )


class FoodResource(Resource):
    """
    Resource for handling operations on a single food item.
    This includes retrieving, updating, and deleting a food item by its unique ID.
    """

    @cache.cached(timeout=86400)  # Cache GET request for 24 hours (86400 seconds)
    def get(self, food_id):
        """
        Handle GET requests to retrieve a specific food item by its ID.
        :param food_id: The unique identifier of the food item.
        :return: A JSON response with the serialized food object if found, or
                 an error message with HTTP status code 404.
        """
        # Retrieve the food object from the database using its unique ID
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
        # Extract the JSON payload from the incoming request
        data = request.get_json()
        # Update the food item using the provided data; returns the updated Food object
        food = update_food(food_id, **data)
        # Serialize and return the updated food object with status code 200 (OK)
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
        # Delete the food item from the database using its unique ID
        delete_food(food_id)
        # Return a response indicating successful deletion with status code 204
        return Response(
            "Food Item Deleted",
            204,
            mimetype="application/json"
        )
