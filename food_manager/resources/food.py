"""
Module for Food API endpoints.

This module defines resources for handling food items, including
retrieving, creating, updating, and deleting them.
"""
import os

from flasgger import swag_from
from flask import request, url_for, make_response, Response
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound

from food_manager.builder import FoodManagerBuilder
from food_manager.constants import NAMESPACE, LINK_RELATIONS_URL, FOOD_PROFILE, DOC_FOLDER
from food_manager.db_operations import (
    create_food, get_food_by_id, get_all_foods, update_food, delete_food
)
from food_manager.models import Food
from food_manager.utils.reponses import create_json_response, internal_server_error, error_response
from food_manager.utils.cache import class_cache


@class_cache
class FoodListResource(Resource):
    """
    Resource for handling operations on the list of food items.
    This includes retrieving all food items (GET) and creating a new food item (POST).
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}food/FoodListResource/get.yml")
    def get(self):
        """
        Handle GET requests to retrieve all food items.
        :return: A JSON response containing a list of serialized food objects with
                 HTTP status code 200.
        """

        self_url = url_for("api.foodlistresource")
        builder = FoodManagerBuilder()
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", self_url)
        builder.add_control("profile", href=FOOD_PROFILE)
        builder.add_control_add_food()
        builder.add_control_all_recipes()
        try:
            items = get_all_foods()
            serialized_items = [item.serialize() for item in items]
            builder["items"] = serialized_items
            return create_json_response(builder)
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}food/FoodListResource/post.yml")
    def post(self):
        """
        Handle POST requests to create a new food item.
        :return: A JSON response with the serialized new food object, or an error
                 message if creation fails.
        """
        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()
        try:
            validate(data, Food.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            created_food = create_food(data.get("name"), data.get("description"), data.get("image_url"))
            response = make_response(create_json_response(created_food.serialize(), 201))
            response.headers["Location"] = url_for("api.foodresource", food_id=created_food)
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
class FoodResource(Resource):
    """
    Resource for handling operations on a single food item.
    This includes retrieving, updating, and deleting a food item by its unique ID.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}food/FoodResource/get.yml")
    def get(self, food_id):
        """
        Handle GET requests to retrieve a specific food item by its ID.
        :param food_id: The unique identifier of the food item.
        :return: A JSON response with the serialized food object if found, or
                 an error message with HTTP status code 404.
        """

        try:
            food = get_food_by_id(food_id)
            return create_json_response(food.serialize())
        except NotFound:
            return error_response(
                title="Food not found",
                message=f"No food item with ID {food_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}food/FoodResource/put.yml")
    def put(self, food_id):
        """
        Handle PUT requests to update an existing food item.
        :param food_id: The unique identifier of the food item to update.
        :return: A JSON response with the serialized updated food object and
                 HTTP status code 200.
        """

        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()

        try:
            validate(data, Food.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            updated_food = update_food(
                food_id=food_id,
                name=data.get("name"),
                description=data.get("description"),
                image_url=data.get("image_url")
            )
            return create_json_response(updated_food.serialize())
        except NotFound:
            return error_response(
                title="Food not found",
                message=f"No food item with ID {food_id}",
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

    @swag_from(os.getcwd() + f"{DOC_FOLDER}food/FoodResource/delete.yml")
    def delete(self, food_id):
        """
        Handle DELETE requests to remove a specific food item by its ID.
        :param food_id: The unique identifier of the food item to delete.
        :return: A response indicating that the food item was deleted, with
                    HTTP status code 204 (No Content).
        """
        try:
            delete_food(food_id)
            return Response("", 204)
        except NotFound:
            return error_response(
                title="Food not found",
                message=f"No food item with ID {food_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)
