"""
This module contains unit tests for the custom URL converters used in the Food Manager application.

The tests ensure that the `to_url()` method of each converter correctly returns the expected string
representation of the model's primary key, which is critical for proper URL generation and
Flask routing.
"""

from food_manager.converters.category import CategoryConverter
from food_manager.converters.food import FoodConverter
from food_manager.converters.ingredient import IngredientConverter
from food_manager.converters.nutritional_info import NutritionalInfoConverter
from food_manager.converters.recipe import RecipeConverter
from food_manager.models import (
    Category,
    Food,
    Ingredient,
    NutritionalInfo,
    Recipe,
)

class TestToUrlConverters:
    """
    Unit tests for custom URL converters' to_url() methods.

    These tests validate that converters return the correct string
    representations of primary keys from model instances.
    """

    def test_category_converter_to_url(self):
        """
        Test that CategoryConverter.to_url returns the correct category_id as a string.
        """
        category = Category(category_id=1, name="Italian", description="Italian dishes")
        converter = CategoryConverter()
        assert converter.to_url(category) == "1"

    def test_food_converter_to_url(self):
        """
        Test that FoodConverter.to_url returns the correct food_id as a string.
        """
        food = Food(food_id=1, name="Pizza", description="Cheesy pizza", image_url="pizza.jpg")
        converter = FoodConverter()
        assert converter.to_url(food) == "1"

    def test_ingredient_converter_to_url(self):
        """
        Test that IngredientConverter.to_url returns the correct ingredient_id as a string.
        """
        ingredient = Ingredient(ingredient_id=1, name="Cheese", image_url="cheese.jpg")
        converter = IngredientConverter()
        assert converter.to_url(ingredient) == "1"

    def test_nutritional_info_converter_to_url(self):
        """
        Test that NutritionalInfoConverter.to_url returns the correct recipe_id as a string.
        """
        info = NutritionalInfo(
            nutritional_info_id=7,
            recipe_id=7,
            calories=100,
            protein=5.0,
            carbs=10.0,
            fat=3.0
        )
        converter = NutritionalInfoConverter()
        assert converter.to_url(info) == "7"

    def test_recipe_converter_to_url(self):
        """
        Test that RecipeConverter.to_url returns the correct recipe_id as a string.
        """
        recipe = Recipe(
            recipe_id=42,
            food_id=1,
            instruction="Mix ingredients",
            prep_time=10,
            cook_time=15,
            servings=2
        )
        converter = RecipeConverter()
        assert converter.to_url(recipe) == "42"
