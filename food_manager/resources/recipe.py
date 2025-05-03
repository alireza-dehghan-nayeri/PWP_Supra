"""
Module for Recipe API endpoints.

This module defines resources for handling recipes and their associations.
"""

from flask import Response, request
import json
from flask_restful import Resource
from food_manager.db_operations import (
    create_recipe, get_recipe_by_id, get_all_recipes, update_recipe, delete_recipe,
    add_ingredient_to_recipe, update_recipe_ingredient, remove_ingredient_from_recipe,
    add_category_to_recipe, remove_category_from_recipe
)
from food_manager.utils.reponses import ResourceMixin, internal_server_error
from food_manager.utils.cache import class_cache


# Recipe Resources
@class_cache
class RecipeListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of recipes.
    Supports GET for retrieving all recipes and POST for creating a new recipe.
    """


    def get(self):
        """
        Handle GET requests to retrieve all recipes.
        :return: A JSON response containing a list of serialized recipe objects
                 with HTTP status code 200.
        """
        return self.handle_get_all(get_all_recipes)


    def post(self):
        """
        Handle POST requests to create a new recipe.
        :return: A JSON response with the serialized new recipe object on success,
                 or an error message if recipe creation fails.
        """
        return self.handle_create(create_recipe, request.json)


@class_cache
class RecipeResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single recipe identified by its recipe_id.
    Supports GET for retrieving, PUT for updating, and DELETE for deleting a recipe.
    """


    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        return self.handle_get_by_id(get_recipe_by_id, recipe_id)


    def put(self, recipe_id):
        """
        Handle PUT requests to update an existing recipe.
        :param recipe_id: The unique identifier of the recipe to update.
        :return: A JSON response with the serialized updated recipe object,
                 or an error message if the update fails.
        """
        return self.handle_update(update_recipe, recipe_id, request.get_json())


    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe to delete.
        :return: An empty response with status code 204 (No Content) on successful deletion,
                 or an error message if deletion fails.
        """
        return self.handle_delete(delete_recipe, recipe_id)


# Recipe-Ingredient Resource
@class_cache
class RecipeIngredientResource(Resource):
    """
    Resource for managing ingredients associated with a specific recipe.
    Supports POST for adding, GET for retrieving, PUT for updating, and DELETE for
    removing an ingredient from a recipe.
    """


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


    def put(self, recipe_id):
        """
        Handle PUT requests to update an ingredient's details within a recipe.
        Expects JSON data with 'ingredient_id', and optionally 'quantity' and 'unit'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the ingredient is updated,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit")

        if not ingredient_id:
            return Response(
                json.dumps({"error": "ingredient_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            update_recipe_ingredient(recipe_id, ingredient_id, quantity, unit)
            return Response(
                json.dumps({
                    "message": "Ingredient updated successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)


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


# Recipe-Category Resource
@class_cache
class RecipeCategoryResource(Resource):
    """
    Resource for managing categories associated with a specific recipe.
    Supports POST for adding a category to a recipe, GET for retrieving a recipe with
    categories, and DELETE for removing a category from a recipe.
    """


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