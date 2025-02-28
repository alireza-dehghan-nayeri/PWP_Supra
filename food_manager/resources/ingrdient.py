from flask import Response, json
from flask import request, jsonify
from flask_restful import Resource
from food_manager.db_operations import (
    create_ingredient, get_ingredient_by_id, get_all_ingredients, update_ingredient, delete_ingredient
    )

class IngredientListResource(Resource):
    def get(self):
        try:
            ingredients = get_all_ingredients()  # Assuming this returns a list of Ingredient objects
            return Response(json.dumps([ingredient.serialize() for ingredient in ingredients]), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def post(self):
        data = request.get_json()
        try:
            ingredient = create_ingredient(**data)  # Assuming this creates and returns an Ingredient object
            return Response(json.dumps(ingredient.serialize()), 201, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

class IngredientResource(Resource):
    def get(self, ingredient_id):
        ingredient = get_ingredient_by_id(ingredient_id)  # Assuming this returns an Ingredient object
        if ingredient:
            return Response(json.dumps(ingredient.serialize()), 200, mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Ingredient not found"}), 404, mimetype="application/json")

    def put(self, ingredient_id):
        data = request.get_json()
        try:
            ingredient = update_ingredient(ingredient_id, **data)  # Assuming this returns an updated Ingredient object
            return Response(json.dumps(ingredient.serialize()), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, ingredient_id):
        try:
            delete_ingredient(ingredient_id)  # Assuming this deletes the ingredient from DB
            return Response("", 204)  # No content response
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
