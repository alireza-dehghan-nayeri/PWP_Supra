"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""

from flask_restful import Resource
from flask import request
from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category,
    delete_category
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# Category Resources
@class_cache
class CategoryListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of categories.
    This includes retrieving all categories (GET) and creating a new category (POST).
    """

    def get(self):
        """
        Handle GET requests to retrieve all categories.
        :return: A JSON response with a list of serialized category objects or an error
                 message.
        """
        return self.handle_get_all(get_all_categories)

    def post(self):
        """
        Handle POST requests to create a new category.
        :return: A JSON response with the serialized new category or an error message.
        """
        return self.handle_create(create_category, request.get_json())


@class_cache
class CategoryResource(Resource, ResourceMixin):
    """
    Resource for handling operations in a single category.
    This includes retrieving, updating, and deleting a category by its ID.
    """

    def get(self, category_id):
        """
        Handle GET requests to retrieve a specific category by its ID.
        :param category_id: The ID of the category to retrieve.
        :return: A JSON response with the serialized category object, or an error
                 message if not found.
        """
        return self.handle_get_by_id(get_category_by_id, category_id, "Category not found")

    def put(self, category_id):
        """
        Handle PUT requests to update an existing category.
        :param category_id: The ID of the category to update.
        :return: A JSON response with the serialized updated category or an error message.
        """
        return self.handle_update(update_category, category_id, request.json)

    def delete(self, category_id):
        """
        Handle DELETE requests to remove a specific category by its ID.
        :param category_id: The ID of the category to delete.
        :return: An empty response with status 204 on success or an error message.
        """
        return self.handle_delete(delete_category, category_id)