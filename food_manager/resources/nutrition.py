"""
Module for Nutritional Information API endpoints.

This module defines resources for handling nutritional information items.
It supports GET (list and detail), POST, PUT, and DELETE operations.
"""

from flask import request, url_for, make_response, Response
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound

from food_manager.builder import FoodManagerBuilder
from food_manager.constants import NAMESPACE, LINK_RELATIONS_URL, NUTRITION_PROFILE
from food_manager.db_operations import (
    create_nutritional_info, get_all_nutrition, get_nutritional_info_by_id,
    update_nutritional_info, delete_nutritional_info
)
from food_manager.models import NutritionalInfo
from food_manager.utils.reponses import create_json_response, internal_server_error, error_response
from food_manager.utils.cache import class_cache


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

        self_url = url_for("api.nutritionalinfolistresource")
        builder = FoodManagerBuilder()
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", self_url)
        builder.add_control("profile", href=NUTRITION_PROFILE)
        builder.add_control_add_nutritional_info()
        builder.add_control_all_recipes()
        try:
            items = get_all_nutrition()
            serialized_items = [item.serialize() for item in items]
            builder["items"] = serialized_items
            return create_json_response(builder)
        except Exception as e:
            return internal_server_error(e)

    def post(self):
        """
        Handle POST requests to create a new nutritional information item.
        :return: A JSON response with the serialized new nutritional info object or 
                 an error message if creation fails.
        """
        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()
        try:
            validate(data, NutritionalInfo.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            created_nutritional_info = create_nutritional_info(
                data.get("recipe_id"),
                data.get("calories"),
                data.get("protein"),
                data.get("carbs"),
                data.get("fat")
            )
            response = make_response(create_json_response(created_nutritional_info.serialize(), 201))
            response.headers["Location"] = url_for(
                "api.nutritionalinforesource",
                nutritional_info_id=created_nutritional_info
            )
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
            return create_json_response(nutritional_info.serialize())
        except NotFound:
            return error_response(
                title="Nutritional info not found",
                message=f"No nutritional info item with ID {nutritional_info_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)

    def put(self, nutritional_info_id):
        """
        Handle PUT requests to update an existing nutritional info item.
        :param nutritional_info_id: The unique identifier of the nutritional info item to update.
        :return: A JSON response with the serialized updated nutritional info object,
                 or an error message if the update fails.
        """

        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()

        try:
            validate(data, NutritionalInfo.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            updated_nutritional_info = update_nutritional_info(
                nutritional_info_id=nutritional_info_id,
                calories=data.get("calories"),
                protein=data.get("protein"),
                carbs=data.get("carbs"),
                fat=data.get("fat")
            )
            return create_json_response(updated_nutritional_info.serialize())
        except NotFound:
            return error_response(
                title="Nutritional info not found",
                message=f"No nutritional info item with ID {nutritional_info_id}",
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
        except NotFound:
            return error_response(
                title="Nutritional info not found",
                message=f"No Nutritional info item with ID {nutritional_info_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)
