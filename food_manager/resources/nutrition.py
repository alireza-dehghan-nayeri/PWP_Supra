"""
Module for Nutritional Information API endpoints.

This module defines resources for handling nutritional information items.
It supports GET (list and detail), POST, PUT, and DELETE operations.
"""

from flask import request
from flask_restful import Resource

from food_manager.db_operations import (
    create_nutritional_info, get_all_nutrition, get_nutritional_info_by_id,
    update_nutritional_info, delete_nutritional_info
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# NutritionalInfo Resources
@class_cache
class NutritionalInfoListResource(Resource, ResourceMixin):
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
        return self.handle_get_all(get_all_nutrition)


    def post(self):
        """
        Handle POST requests to create a new nutritional information item.
        :return: A JSON response with the serialized new nutritional info object or 
                 an error message if creation fails.
        """
        return self.handle_create(create_nutritional_info, request.get_json())


@class_cache
class NutritionalInfoResource(Resource, ResourceMixin):
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
        return self.handle_get_by_id(get_nutritional_info_by_id, nutritional_info_id)


    def put(self, nutritional_info_id):
        """
        Handle PUT requests to update an existing nutritional info item.
        :param nutritional_info_id: The unique identifier of the nutritional info item to update.
        :return: A JSON response with the serialized updated nutritional info object,
                 or an error message if the update fails.
        """
        return self.handle_update(update_nutritional_info, nutritional_info_id)


    def delete(self, nutritional_info_id):
        """
        Handle DELETE requests to remove a specific nutritional info item by its ID.
        :param nutritional_info_id: The unique identifier of the nutritional info item to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is successful,
                 or an error message if deletion fails.
        """
        return self.handle_delete(delete_nutritional_info, nutritional_info_id)