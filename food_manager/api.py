from flask import Blueprint
from flask_restful import Api
from food_manager.resources.category import *
from food_manager.resources.recipe import *
from food_manager.resources.food import *
from food_manager.resources.ingredient import *
from food_manager.resources.nutrition import *

# Define the API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

# Create a custom BaseConverter that returns a Food object


# Food Endpoints
api.add_resource(FoodListResource, "/foods/")
api.add_resource(FoodResource, "/foods/<food:food_id>/")  # Use 'food' converter here

# Recipe Endpoints
api.add_resource(RecipeListResource, "/recipes/")
api.add_resource(RecipeResource, "/recipes/<recipe:recipe_id>/")
api.add_resource(RecipeIngredientResource, "/recipes/<recipe:recipe_id>/ingredients/")
api.add_resource(RecipeCategoryResource, "/recipes/<recipe:recipe_id>/categories/")

# Ingredient Endpoints
api.add_resource(IngredientListResource, "/ingredients/")
api.add_resource(IngredientResource, "/ingredients/<ingredient:ingredient_id>/")

# Category Endpoints
api.add_resource(CategoryListResource, "/categories/")
api.add_resource(CategoryResource, "/categories/<category:category_id>/")

# Nutritional Info Endpoint
api.add_resource(NutritionalInfoListResource, "/nutritional-info/")
api.add_resource(NutritionalInfoResource, "/nutritional-info/<nutritional_info:nutritional_info_id>/")
