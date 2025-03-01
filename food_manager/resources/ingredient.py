# Import necessary modules and functions from Flask and flask_restful
from flask import Response, json, request, jsonify
from flask_restful import Resource
# Import database operations for ingredient management
from food_manager.db_operations import create_ingredient, get_ingredient_by_id, get_all_ingredients, update_ingredient, delete_ingredient
from food_manager import cache  # Import cache for caching responses

# Define resource for handling list operations on ingredients (retrieve all, create new)
class IngredientListResource(Resource):
    @cache.cached(timeout=86400)  # Cache the result of the GET request for 24 hours (86400 seconds)
    def get(self):
        """
        Handle GET requests to retrieve all ingredient items.
        :return: A JSON response containing a list of serialized ingredient objects, or an error message.
        """
        try:
            # Retrieve all ingredient objects from the database
            ingredients = get_all_ingredients()  # Assuming this returns a list of Ingredient objects
            # Serialize each ingredient object and return the list as a JSON response with HTTP status code 200
            return Response(json.dumps([ingredient.serialize() for ingredient in ingredients]), 200, mimetype="application/json")
        except Exception as e:
            # In case of an exception, return an error message with HTTP status code 500 (Internal Server Error)
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def post(self):
        """
        Handle POST requests to create a new ingredient.
        :return: A JSON response with the serialized newly created ingredient object, or an error message.
        """
        # Retrieve JSON data sent in the request body
        data = request.get_json()
        try:
            # Create a new ingredient using the provided data and return the created Ingredient object
            ingredient = create_ingredient(**data)  # Assuming this creates and returns an Ingredient object
            # Serialize the new ingredient and return as JSON with HTTP status code 201 (Created)
            return Response(json.dumps(ingredient.serialize()), 201, mimetype="application/json")
        except Exception as e:
            # In case of an exception, return an error message with HTTP status code 500 (Internal Server Error)
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

# Define resource for handling operations on a single ingredient (retrieve, update, delete)
class IngredientResource(Resource):
    @cache.cached(timeout=86400)  # Cache the result of the GET request for 24 hours (86400 seconds)
    def get(self, ingredient_id):
        """
        Handle GET requests to retrieve a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to retrieve.
        :return: A JSON response with the serialized ingredient object or an error message if not found.
        """
        # Retrieve the ingredient object using its ID
        ingredient = get_ingredient_by_id(ingredient_id)  # Assuming this returns an Ingredient object
        if ingredient:
            # If found, serialize the ingredient and return it with HTTP status code 200 (OK)
            return Response(json.dumps(ingredient.serialize()), 200, mimetype="application/json")
        else:
            # If not found, return an error message with HTTP status code 404 (Not Found)
            return Response(json.dumps({"error": "Ingredient not found"}), 404, mimetype="application/json")

    def put(self, ingredient_id):
        """
        Handle PUT requests to update an existing ingredient.
        :param ingredient_id: The ID of the ingredient to update.
        :return: A JSON response with the serialized updated ingredient object or an error message.
        """
        # Retrieve JSON data sent in the request body for updating the ingredient
        data = request.get_json()
        try:
            # Update the ingredient using the provided data and return the updated Ingredient object
            ingredient = update_ingredient(ingredient_id, **data)  # Assuming this returns an updated Ingredient object
            # Serialize the updated ingredient and return it with HTTP status code 200 (OK)
            return Response(json.dumps(ingredient.serialize()), 200, mimetype="application/json")
        except Exception as e:
            # In case of an exception, return an error message with HTTP status code 500 (Internal Server Error)
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, ingredient_id):
        """
        Handle DELETE requests to remove a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is successful, or an error message.
        """
        try:
            # Delete the ingredient from the database using its ID
            delete_ingredient(ingredient_id)  # Assuming this deletes the ingredient from the DB
            # Return an empty response with HTTP status code 204 (No Content) indicating successful deletion
            return Response("", 204)
        except Exception as e:
            # In case of an exception, return an error message with HTTP status code 500 (Internal Server Error)
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
