"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""
import os

from flasgger import swag_from
from flask_restful import Resource
from flask import request, url_for, make_response, Response
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound

from food_manager.builder import FoodManagerBuilder
from food_manager.constants import NAMESPACE, LINK_RELATIONS_URL, CATEGORY_PROFILE, DOC_FOLDER

from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category,
    delete_category
)
from food_manager.models import Category
from food_manager.utils.reponses import create_json_response, internal_server_error, error_response
from food_manager.utils.cache import class_cache


@class_cache
class CategoryListResource(Resource):
    """
    Resource for handling operations on the list of categories.
    This includes retrieving all categories (GET) and creating a new category (POST).
    """
    @swag_from(os.getcwd() + f"{DOC_FOLDER}category/CategoryListResource/get.yml")
    def get(self):
        """
        Handle GET requests to retrieve all categories.
        :return: A JSON response with a list of serialized category objects or an error
                 message.
        """

        self_url = url_for("api.categorylistresource")
        builder = FoodManagerBuilder()
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", self_url)
        builder.add_control("profile", href=CATEGORY_PROFILE)
        builder.add_control_add_category()
        builder.add_control_all_recipes()
        try:
            items = get_all_categories()
            serialized_items = [item.serialize() for item in items]
            builder["items"] = serialized_items
            return create_json_response(builder)
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}category/CategoryListResource/post.yml")
    def post(self):
        """
        Handle POST requests to create a new category.
        :return: A JSON response with the serialized new category or an error message.
        """
        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()
        try:
            validate(data, Category.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            created_category = create_category(data.get("name"), data.get("description"))
            response = make_response(create_json_response(created_category.serialize(), 201))
            response.headers["Location"] = url_for("api.categoryresource", category_id=created_category)
            return response
        except ValueError as ve:
            return error_response(
                title="Conflict",
                message=str(ve),
                status_code=409
            )
        except Exception as e:
            return internal_server_error(e)


@class_cache
class CategoryResource(Resource):
    """
    Resource for handling operations in a single category.
    This includes retrieving, updating, and deleting a category by its ID.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}category/CategoryResource/get.yml")
    def get(self, category_id):
        """
        Handle GET requests to retrieve a specific category by its ID.
        :param category_id: The ID of the category to retrieve.
        :return: A JSON response with the serialized category object, or an error
                 message if not found.
        """

        try:
            category = get_category_by_id(category_id)
            return create_json_response(category.serialize())
        except NotFound:
            return error_response(
                title="Category not found",
                message=f"No category item with ID {category_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}category/CategoryResource/put.yml")
    def put(self, category_id):
        """
        Handle PUT requests to update an existing category.
        :param category_id: The ID of the category to update.
        :return: A JSON response with the serialized updated category or an error message.
        """

        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()

        try:
            validate(data, Category.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            updated_category = update_category(
                category_id=category_id,
                name=data.get("name"),
                description=data.get("description")
            )
            return create_json_response(updated_category.serialize())
        except NotFound:
            return error_response(
                title="Category not found",
                message=f"No category item with ID {category_id}",
                status_code=404
            )
        except ValueError as ve:
            return error_response(
                title="Conflict",
                message=str(ve),
                status_code=409
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}category/CategoryResource/delete.yml")
    def delete(self, category_id):
        """
        Handle DELETE requests to remove a specific category by its ID.
        :param category_id: The ID of the category to delete.
        :return: An empty response with status 204 on success or an error message.
        """
        try:
            delete_category(category_id)
            return Response("", 204)
        except NotFound:
            return error_response(
                title="Category not found",
                message=f"No category item with ID {category_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)
