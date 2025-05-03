"""API module for Food Manager.

This module defines a Flask blueprint for the RESTful API endpoints and maps each
endpoint to its corresponding resource class.
"""

# Import the necessary modules for creating a blueprint and RESTful API.
from flask import Blueprint
from flask_restful import Api
from food_manager.resources.category import CategoryListResource, CategoryResource
from food_manager.resources.recipe import RecipeCategoryResource, RecipeListResource
from food_manager.resources.recipe import RecipeResource, RecipeIngredientResource
from food_manager.resources.food import FoodListResource, FoodResource
from food_manager.resources.ingredient import IngredientListResource, IngredientResource
from food_manager.resources.nutrition import NutritionalInfoListResource, NutritionalInfoResource

# ------------------------------------------------------------------------------
# Blueprint and API Instance Creation
# ------------------------------------------------------------------------------

# Define the API blueprint.
# This blueprint will be registered with the Flask application under the URL prefix "/api".
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Create a Flask-RESTful API instance using the defined blueprint.
api = Api(api_bp)

# ------------------------------------------------------------------------------
# API Endpoint Registration
# ------------------------------------------------------------------------------
# Each API endpoint is mapped to a corresponding resource class.
# URL converters (e.g., <food:food_id>) are used to ensure proper conversion
# of URL parameters when accessing these endpoints.
# ------------------------------------------------------------------------------

# Food Endpoints
# Endpoint for listing all food items and creating a new food item.
api.add_resource(FoodListResource, "/foods/")
# Endpoint for retrieving, updating, or deleting a specific food item.
# The 'food' converter is used to parse the food_id parameter.
api.add_resource(FoodResource, "/foods/<food:food_id>/")

# Recipe Endpoints
# Endpoint for listing all recipes and creating a new recipe.
api.add_resource(RecipeListResource, "/recipes/")
# Endpoint for retrieving, updating, or deleting a specific recipe.
# The 'recipe' converter is used to parse the recipe_id parameter.
api.add_resource(RecipeResource, "/recipes/<recipe:recipe_id>/")
# Endpoint for managing ingredients within a specific recipe (e.g., add, get, update, delete).
api.add_resource(RecipeIngredientResource, "/recipes/<recipe:recipe_id>/ingredients/")
# Endpoint for managing categories associated with a specific recipe (e.g., add, get, delete).
api.add_resource(RecipeCategoryResource, "/recipes/<recipe:recipe_id>/categories/")

# Ingredient Endpoints
# Endpoint for listing all ingredients and creating a new ingredient.
api.add_resource(IngredientListResource, "/ingredients/")
# Endpoint for retrieving, updating, or deleting a specific ingredient.
# The 'ingredient' converter is used to parse the ingredient_id parameter.
api.add_resource(IngredientResource, "/ingredients/<ingredient:ingredient_id>/")

# Category Endpoints
# Endpoint for listing all categories and creating a new category.
api.add_resource(CategoryListResource, "/categories/")
# Endpoint for retrieving, updating, or deleting a specific category.
# The 'category' converter is used to parse the category_id parameter.
api.add_resource(CategoryResource, "/categories/<category:category_id>/")

# Nutritional Info Endpoints
# Endpoint for listing all nutritional info items and creating a new nutritional info record.
api.add_resource(NutritionalInfoListResource, "/nutritional-info/")
# Endpoint for retrieving, updating, or deleting a specific nutritional info record.
# The 'nutritional_info' converter is used to parse the nutritional_info_id parameter.
api.add_resource(
    NutritionalInfoResource,"/nutritional-info/<nutritional_info:nutritional_info_id>/"
)
