"""
Module for Recipe API endpoints.

This module defines resources for handling recipes and their associations.
"""
import os

from flasgger import swag_from
from flask import Response, request, url_for, make_response
import json
from flask_restful import Resource
from jsonschema import validate, ValidationError
from werkzeug.exceptions import NotFound

from food_manager.builder import FoodManagerBuilder
from food_manager.constants import NAMESPACE, LINK_RELATIONS_URL, RECIPE_PROFILE, DOC_FOLDER
from food_manager.db_operations import (
    create_recipe, get_recipe_by_id, get_all_recipes, update_recipe, delete_recipe,
    add_ingredient_to_recipe, update_recipe_ingredient, remove_ingredient_from_recipe,
    add_category_to_recipe, remove_category_from_recipe
)
from food_manager.models import Recipe
from food_manager.utils.reponses import internal_server_error, create_json_response, error_response
from food_manager.utils.cache import class_cache


@class_cache
class RecipeListResource(Resource):
    """
    Resource for handling operations on the list of recipes.
    Supports GET for retrieving all recipes and POST for creating a new recipe.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeListResource/get.yml")
    def get(self):
        """
        Handle GET requests to retrieve all recipes.
        :return: A JSON response containing a list of serialized recipe objects
                 with HTTP status code 200.
        """

        self_url = url_for("api.recipelistresource")
        builder = FoodManagerBuilder()
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", self_url)
        builder.add_control("profile", href=RECIPE_PROFILE)
        builder.add_control_add_recipe()
        builder.add_control_all_foods()
        builder.add_control_all_categories()
        builder.add_control_all_ingredients()

        try:
            items = get_all_recipes()
            serialized_items = [item.serialize() for item in items]
            builder["items"] = serialized_items
            return create_json_response(builder)
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeListResource/post.yml")
    def post(self):
        """
        Handle POST requests to create a new recipe.
        :return: A JSON response with the serialized new recipe object on success,
                 or an error message if recipe creation fails.
        """
        if not request.is_json:
            return error_response(
                title="Unsupported Media Type",
                message="Request must be in application/json format",
                status_code=415
            )

        data = request.get_json()
        try:
            validate(data, Recipe.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            created_recipe = create_recipe(
                data.get("food_id"),
                data.get("instruction"),
                data.get("prep_time"),
                data.get("cook_time"),
                data.get("servings")
            )
            response = make_response(create_json_response(created_recipe.serialize(), 201))
            response.headers["Location"] = url_for("api.reciperesource", recipe_id=created_recipe)
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
class RecipeResource(Resource):
    """
    Resource for handling operations on a single recipe identified by its recipe_id.
    Supports GET for retrieving, PUT for updating, and DELETE for deleting a recipe.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeResource/get.yml")
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """

        try:
            recipe = get_recipe_by_id(recipe_id)
            return create_json_response(recipe.serialize())
        except NotFound:
            return error_response(
                title="Recipe not found",
                message=f"No Recipe item with ID {recipe_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeResource/put.yml")
    def put(self, recipe_id):
        """
        Handle PUT requests to update an existing recipe.
        :param recipe_id: The unique identifier of the recipe to update.
        :return: A JSON response with the serialized updated recipe object,
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
            validate(data, Recipe.get_schema())
        except ValidationError as e:
            return error_response(
                title="Invalid input",
                message=e.message,
                status_code=400
            )

        try:
            updated_recipe = update_recipe(
                recipe_id=recipe_id,
                food_id=data.get("food_id"),
                instruction=data.get("instruction"),
                prep_time=data.get("prep_time"),
                cook_time=data.get("cook_time"),
                servings=data.get("servings")
            )
            return create_json_response(updated_recipe.serialize())
        except NotFound:
            return error_response(
                title="Recipe not found",
                message=f"No Recipe item with ID {recipe_id}",
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

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeResource/delete.yml")
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe to delete.
        :return: An empty response with status code 204 (No Content) on successful deletion,
                 or an error message if deletion fails.
        """

        try:
            delete_recipe(recipe_id)
            return Response("", 204)
        except NotFound:
            return error_response(
                title="Recipe not found",
                message=f"No Recipe item with ID {recipe_id}",
                status_code=404
            )
        except Exception as e:
            return internal_server_error(e)


@class_cache
class RecipeIngredientResource(Resource):
    """
    Resource for managing ingredients associated with a specific recipe.
    Supports POST for adding, GET for retrieving, PUT for updating, and DELETE for
    removing an ingredient from a recipe.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeIngredientResource/post.yml")
    def post(self, recipe_id):
        """
        Handle POST requests to add an ingredient to a recipe.
        Expects JSON data with 'ingredient_id', 'quantity', and optionally 'unit'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message and status code 201 if the ingredient
                 is added, or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit", "piece")

        if not ingredient_id or not quantity:
            return Response(
                json.dumps({"error": "ingredient_id and quantity are required."}),
                400,
                mimetype="application/json"
            )

        try:
            add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit)
            return Response(
                json.dumps({
                    "message": "Ingredient added successfully!",
                    "recipe_id": recipe_id
                }),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeIngredientResource/get.yml")
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe (including its ingredients).
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            return Response(
                json.dumps(recipe.serialize()),
                200,
                mimetype="application/json"
            )
        return Response(
            json.dumps({"error": "Recipe not found"}),
            404,
            mimetype="application/json"
        )


    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeIngredientResource/delete.yml")
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove an ingredient from a recipe.
        Expects JSON data with 'ingredient_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the ingredient is removed,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")

        if not ingredient_id:
            return Response(
                json.dumps({"error": "ingredient_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            remove_ingredient_from_recipe(recipe_id, ingredient_id)
            return Response(
                json.dumps({
                    "message": "Ingredient removed successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)


@class_cache
class RecipeCategoryResource(Resource):
    """
    Resource for managing categories associated with a specific recipe.
    Supports POST for adding a category to a recipe, GET for retrieving a recipe with
    categories, and DELETE for removing a category from a recipe.
    """

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeCategoryResource/post.yml")
    def post(self, recipe_id):
        """
        Handle POST requests to add a category to a recipe.
        Expects JSON data with 'category_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the category is added,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        category_id = data.get("category_id")

        if not category_id:
            return Response(
                json.dumps({"error": "category_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            add_category_to_recipe(recipe_id, category_id)
            return Response(
                json.dumps({
                    "message": "Category added successfully!",
                    "recipe_id": recipe_id
                }),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeCategoryResource/get.yml")
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe (including its categories).
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            return Response(
                json.dumps(recipe.serialize()),
                200,
                mimetype="application/json"
            )
        return Response(
            json.dumps({"error": "Recipe not found"}),
            404,
            mimetype="application/json"
        )
    
    @swag_from(os.getcwd() + f"{DOC_FOLDER}recipe/RecipeCategoryResource/delete.yml")
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove a category from a recipe.
        Expects JSON data with 'category_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the category is removed,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        category_id = data.get("category_id")

        if not category_id:
            return Response(
                json.dumps({"error": "category_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            remove_category_from_recipe(recipe_id, category_id)
            return Response(
                json.dumps({
                    "message": "Category removed successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)
