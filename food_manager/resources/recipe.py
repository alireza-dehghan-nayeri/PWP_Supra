from flask import Response, request
import json
from flask_restful import Resource
from food_manager.db_operations import *
from food_manager.models import Recipe

# Recipe Resources
class RecipeListResource(Resource):
    def get(self):
        recipes = [recipe.serialize() for recipe in get_all_recipes()]
        return Response(json.dumps(recipes), 200, mimetype="application/json")

    def post(self):
        data = request.get_json()
        try:
            recipe = create_recipe(**data)
            return Response(json.dumps(recipe.serialize()), 201, mimetype="application/json")
        except ValueError as e:
            return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": "An unexpected error occurred.", "details": str(e)}), 500, mimetype="application/json")

class RecipeResource(Resource):
    def get(self, recipe_id):
        recipe = get_recipe_by_id(recipe_id)  # Fetch recipe by recipe_id
        if recipe:
            return Response(json.dumps(recipe.serialize()), 200, mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Recipe not found"}), 404, mimetype="application/json")

    def put(self, recipe_id):
        data = request.get_json()
        try:
            updated_recipe = update_recipe(recipe_id, **data)  # Update recipe by recipe_id
            return Response(json.dumps(updated_recipe.serialize()), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, recipe_id):
        try:
            delete_recipe(recipe_id)  # Delete recipe by recipe_id
            return Response("", 204, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

# Recipe-Ingredient Resource
class RecipeIngredientResource(Resource):
    def post(self, recipe_id):
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit", "piece")
        
        if not ingredient_id or not quantity:
            return Response(json.dumps({"error": "ingredient_id and quantity are required."}), 400, mimetype="application/json")
        
        try:
            add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit)  # Add ingredient to recipe by recipe_id
            return Response(json.dumps({"message": "Ingredient added successfully!", "recipe_id": recipe_id}), 201, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
        
    def get(self, recipe_id):
        recipe = get_recipe_by_id(recipe_id)  # Fetch recipe by recipe_id
        if recipe:
            return Response(json.dumps(recipe.serialize()), 200, mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Recipe not found"}), 404, mimetype="application/json")

    def put(self, recipe_id):
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit")
        
        if not ingredient_id:
            return Response(json.dumps({"error": "ingredient_id is required."}), 400, mimetype="application/json")
        
        try:
            update_recipe_ingredient(recipe_id, ingredient_id, quantity, unit)  # Update ingredient in recipe by recipe_id
            return Response(json.dumps({"message": "Ingredient updated successfully!", "recipe_id": recipe_id}), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, recipe_id):
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        
        if not ingredient_id:
            return Response(json.dumps({"error": "ingredient_id is required."}), 400, mimetype="application/json")
        
        try:
            remove_ingredient_from_recipe(recipe_id, ingredient_id)  # Remove ingredient from recipe by recipe_id
            return Response(json.dumps({"message": "Ingredient removed successfully!", "recipe_id": recipe_id}), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

        
# Recipe-Category Resource
class RecipeCategoryResource(Resource):
    def post(self, recipe_id):
        data = request.get_json()
        category_id = data.get("category_id")
        
        if not category_id:
            return Response(json.dumps({"error": "category_id is required."}), 400, mimetype="application/json")
        
        try:
            # Ensure you're passing recipe_id correctly
            add_category_to_recipe(recipe_id, category_id)  # Add category to recipe by recipe_id
            return Response(json.dumps({"message": "Category added successfully!", "recipe_id": recipe_id}), 201, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def get(self, recipe_id):
        recipe = get_recipe_by_id(recipe_id)  # Fetch recipe by recipe_id
        if recipe:
            return Response(json.dumps(recipe.serialize()), 200, mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Recipe not found"}), 404, mimetype="application/json")

    def delete(self, recipe_id):
        data = request.get_json()
        category_id = data.get("category_id")
        
        if not category_id:
            return Response(json.dumps({"error": "category_id is required."}), 400, mimetype="application/json")
        
        try:
            # Ensure you're passing recipe_id correctly
            remove_category_from_recipe(recipe_id, category_id)  # Remove category from recipe by recipe_id
            return Response(json.dumps({"message": "Category removed successfully!", "recipe_id": recipe_id}), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
