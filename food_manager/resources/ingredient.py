"""
Module for Ingredient API endpoints.

This module defines resources for handling ingredients, including retrieving,
creating, updating, and deleting them.
"""

from flask import request, url_for, make_response, Response
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound

from food_manager.builder import FoodManagerBuilder
from food_manager.constants import NAMESPACE, LINK_RELATIONS_URL, INGREDIENT_PROFILE
from food_manager.db_operations import (
    create_ingredient,
    get_ingredient_by_id,
    get_all_ingredients,
    update_ingredient,
    delete_ingredient,
)
from food_manager.models import Ingredient
from food_manager.utils.reponses import create_json_response, internal_server_error, error_response
from food_manager.utils.cache import class_cache


@class_cache
class IngredientListResource(Resource):

    def get(self):
        """
        Handle GET requests to retrieve all ingredient items.
        :return: A JSON response containing a list of serialized ingredient objects,
                 or an error message.
        """
        self_url = url_for("api.ingredientlistresource")
        builder = FoodManagerBuilder()
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", self_url)
        builder.add_control("profile", href=INGREDIENT_PROFILE)
        builder.add_control_add_ingredient()
        builder.add_control_all_recipes()
        try:
            items = get_all_ingredients()
            serialized_items = [item.serialize() for item in items]
            builder["items"] = serialized_items
            return create_json_response(builder)
        except Exception as e:
            return internal_server_error(e)

    def post(self):
        """
        Handle POST requests to create a new ingredient.
        :return: A JSON response with the serialized newly created ingredient object,
                 or an error message.
        """

        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()
        try:
            validate(data, Ingredient.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            created_ingredient = create_ingredient(data.get("name"), data.get("image_url"))
            response = make_response(create_json_response(created_ingredient.serialize(), 201))
            response.headers["Location"] = url_for(
                "api.ingredientresource",
                ingredient_id=created_ingredient
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
class IngredientResource(Resource):

    def get(self, ingredient_id):
        """
        Handle GET requests to retrieve a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to retrieve.
        :return: A JSON response with the serialized ingredient object, or an error
                 message if not found.
        """
        try:
            ingredient = get_ingredient_by_id(ingredient_id)
            return create_json_response(ingredient.serialize())
        except NotFound:
            return error_response(
                title="Ingredient not found",
                message=f"No Ingredient item with ID {ingredient_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)

    def put(self, ingredient_id):
        """
        Handle PUT requests to update an existing ingredient.
        :param ingredient_id: The ID of the ingredient to update.
        :return: A JSON response with the serialized updated ingredient object,
                 or an error message.
        """

        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()

        try:
            validate(data, Ingredient.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            updated_ingredient = update_ingredient(
                ingredient_id=ingredient_id,
                name=data.get("name"),
                image_url=data.get("image_url")
            )
            return create_json_response(updated_ingredient.serialize())
        except NotFound:
            return error_response(
                title="Ingredient not found",
                message=f"No ingredient item with ID {ingredient_id}",
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

    def delete(self, ingredient_id):
        """
        Handle DELETE requests to remove a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is
                 successful, or an error message.
        """
        try:
            delete_ingredient(ingredient_id)
            return Response("", 204)
        except NotFound:
            return error_response(
                title="Ingredient not found",
                message=f"No ingredient item with ID {ingredient_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)
