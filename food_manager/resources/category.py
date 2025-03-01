"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""

from flask import Response, json, request, jsonify
from flask_restful import Resource
from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category,
    delete_category
)
from food_manager import cache  # Import cache from food_manager for caching purposes


# Category Resources

class CategoryListResource(Resource):
    """
    Resource for handling operations on the list of categories.
    This includes retrieving all categories (GET) and creating a new category (POST).
    """

    @cache.cached(timeout=86400)  # Cache the result of this method for 24 hours (86400 seconds)
    def get(self):
        """
        Handle GET requests to retrieve all categories.
        :return: A JSON response with a list of serialized category objects or an error
                 message.
        """
        try:
            # Retrieve all category objects from the database
            categories = get_all_categories()  # Returns a list of Category objects
            # Serialize each category and return as a JSON response with status 200
            return Response(
                json.dumps([category.serialize() for category in categories]),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            # If an exception occurs, return an error message with status 500
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def post(self):
        """
        Handle POST requests to create a new category.
        :return: A JSON response with the serialized new category or an error message.
        """
        # Get the JSON data from the request body
        data = request.get_json()
        try:
            # Create a new category using the provided data; returns a Category object
            category = create_category(**data)
            # Serialize the new category and return it with status 201 (Created)
            return Response(
                json.dumps(category.serialize()),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            # If an exception occurs, return an error message with status 500
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )


class CategoryResource(Resource):
    """
    Resource for handling operations on a single category.
    This includes retrieving, updating, and deleting a category by its ID.
    """

    @cache.cached(timeout=86400)  # Cache the result of this method for 24 hours (86400 seconds)
    def get(self, category_id):
        """
        Handle GET requests to retrieve a specific category by its ID.
        :param category_id: The ID of the category to retrieve.
        :return: A JSON response with the serialized category object, or an error
                 message if not found.
        """
        try:
            # Retrieve the category using the provided ID
            category = get_category_by_id(category_id)  # Returns a Category object
            if category:
                return Response(
                    json.dumps(category.serialize()),
                    200,
                    mimetype="application/json"
                )
            return Response(
                json.dumps({"error": "Category not found"}),
                404,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def put(self, category_id):
        """
        Handle PUT requests to update an existing category.
        :param category_id: The ID of the category to update.
        :return: A JSON response with the serialized updated category or an error message.
        """
        # Get the JSON data from the request body
        data = request.get_json()
        try:
            # Update the category using the provided data; returns an updated Category object
            category = update_category(category_id, **data)
            return Response(
                json.dumps(category.serialize()),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )

    def delete(self, category_id):
        """
        Handle DELETE requests to remove a specific category by its ID.
        :param category_id: The ID of the category to delete.
        :return: An empty response with status 204 on success or an error message.
        """
        try:
            # Delete the category using the provided ID
            delete_category(category_id)
            return Response("", 204)
        except Exception as e:
            return Response(
                json.dumps({"error": str(e)}),
                500,
                mimetype="application/json"
            )
