from werkzeug.routing import BaseConverter
from flask import abort
from food_manager.db_operations import get_recipe_by_id, get_ingredient_by_id, get_category_by_id

class RecipeConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert recipe_id to an integer for querying
        return int(value)

    def to_url(self, value):
        # Convert the Recipe object back to recipe_id for URL
        return str(value.recipe_id)  # Assuming recipe is an object with a `recipe_id` attribute

class IngredientConverter(BaseConverter):
    def to_python(self, value):
        ingredient = get_ingredient_by_id(int(value))
        if ingredient is None:
            abort(404, description="Ingredient not found")
        return ingredient

    def to_url(self, value):
        return str(value.ingredient_id)  # or return str(value.id) if different

class CategoryConverter(BaseConverter):
    def to_python(self, value):
        category = get_category_by_id(int(value))
        if category is None:
            abort(404, description="Category not found")
        return category

    def to_url(self, value):
        return str(value.category_id)  # or return str(value.id) if different
