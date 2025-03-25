from sqlalchemy.exc import IntegrityError
from food_manager import db_operations as ops
import pytest
from werkzeug.exceptions import NotFound

class TestDBOperations:
    """Test suite for Food entity operations with valid and edge cases."""

    def test_create_food_success(self, session):
        """Create a food with valid inputs."""
        food = ops.create_food(name="Tomato", description="Fresh", image_url="http://img.com/tomato.jpg")
        assert food.name == "Tomato"
        assert food.description == "Fresh"

    def test_create_food_duplicate_name(self, session):
        """Raise ValueError on duplicate food name."""
        ops.create_food(name="Tomato", description="Fresh", image_url="http://img.com/tomato.jpg")
        with pytest.raises(ValueError):
            ops.create_food(name="Tomato", description="Duplicate", image_url="http://img.com/dupe.jpg")

    def test_get_food_by_id_valid(self, session):
        """Return correct food for a valid ID."""
        food = ops.create_food(name="Potato", description="Starchy", image_url="http://img.com/potato.jpg")
        found = ops.get_food_by_id(food.food_id)
        assert found.name == "Potato"

    def test_get_food_by_id_invalid(self, session):
        """Raise 404 for non-existent food ID."""
        with pytest.raises(NotFound):
            ops.get_food_by_id(99999)

    def test_get_all_foods_returns_list(self, session):
        """Return all foods in a list."""
        ops.create_food(name="Apple", description="Fruit", image_url="http://img.com/apple.jpg")
        ops.create_food(name="Banana", description="Fruit", image_url="http://img.com/banana.jpg")
        foods = ops.get_all_foods()
        assert isinstance(foods, list)
        assert any(f.name == "Apple" for f in foods)
        assert any(f.name == "Banana" for f in foods)

    def test_update_food_success(self, session):
        """Update a food that exists."""
        food = ops.create_food(name="OldName", description="Old", image_url="old.jpg")
        updated = ops.update_food(food.food_id, name="NewName", description="NewDesc", image_url="new.jpg")
        assert updated.name == "NewName"
        assert updated.description == "NewDesc"
        assert updated.image_url == "new.jpg"

    def test_update_food_not_found(self, session):
        """Raise 404 when trying to update non-existent food."""
        with pytest.raises(NotFound):
            ops.update_food(food_id=9999, name="X", description="Y", image_url="Z")

    def test_delete_food_success(self, session):
        """Delete a food that exists and verify it is gone."""
        food = ops.create_food(name="DeleteMe", description="Bye", image_url="bye.jpg")
        ops.delete_food(food.food_id)  # Don't assign
        with pytest.raises(NotFound):
            ops.get_food_by_id(food.food_id)

    def test_delete_food_not_found(self, session):
        """Raise 404 when deleting a non-existent food."""
        with pytest.raises(NotFound):
            ops.delete_food(9999)

    def test_create_recipe_success(self, session):
        """Create a recipe linked to an existing food."""
        food = ops.create_food(name="Soup", description="Hot", image_url="url")
        recipe = ops.create_recipe(
            food_id=food.food_id,
            instruction="Boil and stir.",
            prep_time=10,
            cook_time=15,
            servings=2
        )
        assert recipe.instruction.startswith("Boil")
        assert recipe.servings == 2

    def test_create_recipe_invalid_food_id(self, session):
        """Raise IntegrityError when creating a recipe with invalid food_id."""
        with pytest.raises(IntegrityError):
            ops.create_recipe(
                food_id=9999,
                instruction="Invalid FK",
                prep_time=5,
                cook_time=10,
                servings=1
            )

    def test_get_recipe_by_id_success(self, session):
        """Fetch an existing recipe by ID."""
        food = ops.create_food(name="Stew", description="Thick", image_url="url")
        recipe = ops.create_recipe(food.food_id, "Simmer for 2h", 30, 120, 4)
        fetched = ops.get_recipe_by_id(recipe.recipe_id)
        assert fetched.instruction == "Simmer for 2h"

    def test_get_recipe_by_id_not_found(self, session):
        """Raise 404 if recipe ID not found."""
        with pytest.raises(NotFound):
            ops.get_recipe_by_id(99999)

    def test_get_all_recipes(self, session):
        """Return a list of all recipes."""
        food = ops.create_food(name="Salad", description="Raw", image_url="url")
        ops.create_recipe(food.food_id, "Mix greens", 5, 0, 1)
        ops.create_recipe(food.food_id, "Add dressing", 2, 0, 1)
        all_recipes = ops.get_all_recipes()
        assert isinstance(all_recipes, list)
        assert len(all_recipes) >= 2

    def test_update_recipe_success(self, session):
        """Update an existing recipe."""
        food = ops.create_food(name="Curry", description="Spicy", image_url="url")
        recipe = ops.create_recipe(food.food_id, "Stir occasionally", 15, 25, 3)
        updated = ops.update_recipe(
            recipe.recipe_id,
            food_id=food.food_id,
            instruction="Stir and simmer",
            prep_time=20,
            cook_time=30,
            servings=4
        )
        assert updated.instruction == "Stir and simmer"
        assert updated.servings == 4

    def test_update_recipe_not_found(self, session):
        """Raise 404 if recipe doesn't exist during update."""
        food = ops.create_food(name="Dummy", description="", image_url="x")
        with pytest.raises(NotFound):
            ops.update_recipe(9999, food.food_id, "x", 1, 1, 1)

    def test_delete_recipe_success(self, session):
        """Delete an existing recipe."""
        food = ops.create_food(name="Pizza", description="Baked", image_url="url")
        recipe = ops.create_recipe(food.food_id, "Bake at 200C", 15, 20, 2)
        ops.delete_recipe(recipe.recipe_id)
        with pytest.raises(NotFound):
            ops.get_recipe_by_id(recipe.recipe_id)

    def test_delete_recipe_not_found(self, session):
        """Raise 404 when deleting non-existent recipe."""
        with pytest.raises(NotFound):
            ops.delete_recipe(9999)

    def test_create_ingredient_success(self, session):
        """Create a new ingredient."""
        ing = ops.create_ingredient(name="Carrot", image_url="http://img.com/carrot.jpg")
        assert ing.name == "Carrot"
        assert "carrot" in ing.image_url

    def test_get_ingredient_by_id_valid(self, session):
        """Get an existing ingredient by ID."""
        ing = ops.create_ingredient(name="Onion", image_url="onion.jpg")
        found = ops.get_ingredient_by_id(ing.ingredient_id)
        assert found.name == "Onion"

    def test_get_ingredient_by_id_not_found(self, session):
        """Raise 404 when ingredient is not found."""
        with pytest.raises(NotFound):
            ops.get_ingredient_by_id(99999)

    def test_get_all_ingredients(self, session):
        """List all ingredients."""
        ops.create_ingredient(name="Garlic", image_url="garlic.jpg")
        ops.create_ingredient(name="Chili", image_url="chili.jpg")
        all_ingredients = ops.get_all_ingredients()
        assert isinstance(all_ingredients, list)
        assert any(i.name == "Garlic" for i in all_ingredients)

    def test_update_ingredient_success(self, session):
        """Update an ingredient's fields."""
        ing = ops.create_ingredient(name="Tomato", image_url="t.jpg")
        updated = ops.update_ingredient(ing.ingredient_id, name="Tomatillo", image_url="updated.jpg")
        assert updated.name == "Tomatillo"
        assert updated.image_url == "updated.jpg"

    def test_update_ingredient_not_found(self, session):
        """Raise 404 when updating non-existent ingredient."""
        with pytest.raises(NotFound):
            ops.update_ingredient(9999, name="X", image_url="Y")

    def test_delete_ingredient_success(self, session):
        """Delete an ingredient and confirm removal."""
        ing = ops.create_ingredient(name="Mint", image_url="mint.jpg")
        ops.delete_ingredient(ing.ingredient_id)
        with pytest.raises(NotFound):
            ops.get_ingredient_by_id(ing.ingredient_id)

    def test_delete_ingredient_not_found(self, session):
        """Raise 404 when deleting non-existent ingredient."""
        with pytest.raises(NotFound):
            ops.delete_ingredient(9999)

    def test_create_category_success(self, session):
        """Create a new category."""
        cat = ops.create_category(name="Vegan", description="Plant-based only")
        assert cat.name == "Vegan"
        assert "Plant" in cat.description

    def test_get_category_by_id_valid(self, session):
        """Retrieve a category by ID."""
        cat = ops.create_category(name="Breakfast", description="Morning meals")
        found = ops.get_category_by_id(cat.category_id)
        assert found.name == "Breakfast"

    def test_get_category_by_id_not_found(self, session):
        """Raise 404 when category is not found."""
        with pytest.raises(NotFound):
            ops.get_category_by_id(99999)

    def test_get_all_categories(self, session):
        """Return all categories as a list."""
        ops.create_category(name="Lunch", description="Midday")
        ops.create_category(name="Dinner", description="Evening")
        categories = ops.get_all_categories()
        assert isinstance(categories, list)
        assert any(c.name == "Dinner" for c in categories)

    def test_update_category_success(self, session):
        """Update category name and description."""
        cat = ops.create_category(name="Snack", description="Small meal")
        updated = ops.update_category(cat.category_id, name="Snacks", description="Light meal")
        assert updated.name == "Snacks"
        assert "Light" in updated.description

    def test_update_category_not_found(self, session):
        """Raise 404 when updating non-existent category."""
        with pytest.raises(NotFound):
            ops.update_category(9999, name="X", description="Y")

    def test_delete_category_success(self, session):
        """Delete a category and verify it's gone."""
        cat = ops.create_category(name="Seasonal", description="Winter only")
        ops.delete_category(cat.category_id)
        with pytest.raises(NotFound):
            ops.get_category_by_id(cat.category_id)

    def test_delete_category_not_found(self, session):
        """Raise 404 when deleting a non-existent category."""
        with pytest.raises(NotFound):
            ops.delete_category(9999)

    def test_create_nutritional_info_success(self, session):
        """Create nutritional info for a recipe."""
        food = ops.create_food("Smoothie", "Blended", "url")
        recipe = ops.create_recipe(food.food_id, "Blend it", 5, 0, 1)
        info = ops.create_nutritional_info(recipe.recipe_id, calories=250, protein=5.0, carbs=20.0, fat=2.0)
        assert info.calories == 250
        assert info.recipe_id == recipe.recipe_id

    def test_create_nutritional_info_invalid_recipe(self, session):
        """Raise IntegrityError if recipe_id doesn't exist."""
        with pytest.raises(IntegrityError):
            ops.create_nutritional_info(9999, calories=100, protein=1.0, carbs=2.0, fat=0.5)

    def test_get_nutritional_info_by_id_success(self, session):
        """Get nutritional info by its ID."""
        food = ops.create_food("Shake", "Drink", "url")
        recipe = ops.create_recipe(food.food_id, "Shake well", 2, 0, 1)
        info = ops.create_nutritional_info(recipe.recipe_id, 200, 4.0, 10.0, 1.5)
        found = ops.get_nutritional_info_by_id(info.nutritional_info_id)
        assert found.calories == 200

    def test_get_nutritional_info_by_id_not_found(self, session):
        """Raise 404 for non-existent nutritional info ID."""
        with pytest.raises(NotFound):
            ops.get_nutritional_info_by_id(99999)

    def test_get_recipe_nutritional_info_success(self, session):
        """Return nutritional info using recipe ID."""
        food = ops.create_food("Tea", "Herbal", "url")
        recipe = ops.create_recipe(food.food_id, "Brew", 3, 0, 1)
        info = ops.create_nutritional_info(recipe.recipe_id, 10, 0.2, 0.1, 0.0)
        found = ops.get_recipe_nutritional_info(recipe.recipe_id)
        assert found.nutritional_info_id == info.nutritional_info_id

    def test_get_recipe_nutritional_info_not_found(self, session):
        """Raise 404 if recipe has no nutritional info."""
        food = ops.create_food("Juice", "Orange", "url")
        recipe = ops.create_recipe(food.food_id, "Squeeze", 1, 0, 1)
        with pytest.raises(NotFound):
            ops.get_recipe_nutritional_info(recipe.recipe_id)

    def test_get_all_nutritions(self, session):
        """List all nutritional info records."""
        food = ops.create_food("Energy Bar", "Snack", "url")
        recipe1 = ops.create_recipe(food.food_id, "Mix & bake", 10, 15, 2)
        recipe2 = ops.create_recipe(food.food_id, "No-bake", 5, 0, 1)
        ops.create_nutritional_info(recipe1.recipe_id, 300, 10, 30, 15)
        ops.create_nutritional_info(recipe2.recipe_id, 250, 8, 25, 12)
        results = ops.get_all_nutritions()
        assert isinstance(results, list)
        assert len(results) >= 2

    def test_update_nutritional_info_success(self, session):
        """Update an existing nutritional info record."""
        food = ops.create_food("Protein Shake", "Workout", "url")
        recipe = ops.create_recipe(food.food_id, "Shake hard", 3, 0, 1)
        info = ops.create_nutritional_info(recipe.recipe_id, 180, 15.0, 5.0, 1.0)
        updated = ops.update_nutritional_info(info.nutritional_info_id, 200, 20.0, 8.0, 2.0)
        assert updated.calories == 200
        assert updated.protein == 20.0

    def test_update_nutritional_info_not_found(self, session):
        """Raise 404 when updating non-existent nutritional info."""
        with pytest.raises(NotFound):
            ops.update_nutritional_info(9999, 1, 1, 1, 1)

    def test_delete_nutritional_info_success(self, session):
        """Delete nutritional info and confirm it's gone."""
        food = ops.create_food("Yogurt", "Plain", "url")
        recipe = ops.create_recipe(food.food_id, "Eat chilled", 1, 0, 1)
        info = ops.create_nutritional_info(recipe.recipe_id, 120, 4, 10, 5)
        ops.delete_nutritional_info(info.nutritional_info_id)
        with pytest.raises(NotFound):
            ops.get_nutritional_info_by_id(info.nutritional_info_id)

    def test_delete_nutritional_info_not_found(self, session):
        """Raise 404 when deleting non-existent nutritional info."""
        with pytest.raises(NotFound):
            ops.delete_nutritional_info(9999)

    def test_add_ingredient_to_recipe_success(self, session):
        """Add an ingredient to a recipe with quantity + unit."""
        food = ops.create_food("Cake", "Sweet", "url")
        recipe = ops.create_recipe(food.food_id, "Bake it", 10, 30, 4)
        ing = ops.create_ingredient("Flour", "img")
        link = ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 200, "grams")
        assert link.recipe_id == recipe.recipe_id
        assert link.ingredient_id == ing.ingredient_id
        assert link.quantity == 200
        assert link.unit == "grams"

    def test_add_ingredient_to_recipe_invalid_ids(self, session):
        """Raise IntegrityError if recipe_id or ingredient_id is invalid."""
        with pytest.raises(IntegrityError):
            ops.add_ingredient_to_recipe(recipe_id=9999, ingredient_id=8888, quantity=1, unit="g")

    def test_update_recipe_ingredient_success(self, session):
        """Update quantity/unit for a recipe-ingredient link."""
        food = ops.create_food("Soup", "Warm", "url")
        recipe = ops.create_recipe(food.food_id, "Boil", 5, 15, 3)
        ing = ops.create_ingredient("Salt", "img")
        ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 1, "tsp")
        updated = ops.update_recipe_ingredient(recipe.recipe_id, ing.ingredient_id, 2, "tbsp")
        assert updated.quantity == 2
        assert updated.unit == "tbsp"

    def test_update_recipe_ingredient_invalid(self, session):
        """Raise 404 when updating non-existent recipe-ingredient pair."""
        with pytest.raises(NotFound):
            ops.update_recipe_ingredient(9999, 9999, 5, "g")

    def test_remove_ingredient_from_recipe_success(self, session):
        """Remove an ingredient from a recipe (no return expected)."""
        food = ops.create_food("Pasta", "Italian", "url")
        recipe = ops.create_recipe(food.food_id, "Boil pasta", 10, 15, 2)
        ing = ops.create_ingredient("Olive Oil", "img")
        ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 10, "ml")

        # Just invoke it — don’t check the return
        ops.remove_ingredient_from_recipe(recipe.recipe_id, ing.ingredient_id)

        # Confirm it's removed by expecting a 404 on update
        with pytest.raises(NotFound):
            ops.update_recipe_ingredient(recipe.recipe_id, ing.ingredient_id, 5, "ml")

    def test_remove_ingredient_from_recipe_invalid(self, session):
        """Raise 404 when removing non-existent recipe-ingredient link."""
        with pytest.raises(NotFound):
            ops.remove_ingredient_from_recipe(9999, 9999)


    def test_add_category_to_recipe_success(self, session):
        """Link a category to a recipe."""
        food = ops.create_food("Sandwich", "Snack", "url")
        recipe = ops.create_recipe(food.food_id, "Layer and serve", 5, 0, 1)
        cat = ops.create_category("Quick Meal", "Fast prep")
        link = ops.add_category_to_recipe(recipe.recipe_id, cat.category_id)
        assert link.recipe_id == recipe.recipe_id
        assert link.category_id == cat.category_id

    def test_add_category_to_recipe_invalid_ids(self, session):
        """Raise IntegrityError if recipe_id or category_id is invalid."""
        with pytest.raises(IntegrityError):
            ops.add_category_to_recipe(recipe_id=9999, category_id=8888)

    def test_remove_category_from_recipe_success(self, session):
        """Unlink a category from a recipe (no return expected)."""
        food = ops.create_food("Toast", "Simple", "url")
        recipe = ops.create_recipe(food.food_id, "Toast bread", 2, 1, 1)
        cat = ops.create_category("Breakfast", "Morning meals")
        ops.add_category_to_recipe(recipe.recipe_id, cat.category_id)
        ops.remove_category_from_recipe(recipe.recipe_id, cat.category_id)
        with pytest.raises(NotFound):
            ops.remove_category_from_recipe(recipe.recipe_id, cat.category_id)

    def test_remove_category_from_recipe_not_found(self, session):
        """Raise 404 when removing non-existent category link."""
        with pytest.raises(NotFound):
            ops.remove_category_from_recipe(recipe_id=9999, category_id=9999)

    def test_search_recipes_by_ingredient(self, session):
        """Return recipes that use an ingredient by partial name."""
        food = ops.create_food("Taco", "Mexican", "url")
        recipe = ops.create_recipe(food.food_id, "Fill and fold", 5, 10, 1)
        ing = ops.create_ingredient("Cabbage", "url")
        ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 50, "g")

        matches = ops.search_recipes_by_ingredient("cabb")
        assert any(r.recipe_id == recipe.recipe_id for r in matches)

    def test_search_recipes_by_category(self, session):
        """Return recipes with a category by partial category name."""
        food = ops.create_food("Stew", "Hearty", "url")
        recipe = ops.create_recipe(food.food_id, "Simmer it", 10, 60, 4)
        cat = ops.create_category("Comfort Food", "Warm meals")
        ops.add_category_to_recipe(recipe.recipe_id, cat.category_id)

        results = ops.search_recipes_by_category("comfort")
        assert any(r.recipe_id == recipe.recipe_id for r in results)

    def test_get_recipes_by_food(self, session):
        """Fetch all recipes related to a specific food."""
        food = ops.create_food("Soup", "Hot", "url")
        r1 = ops.create_recipe(food.food_id, "Boil", 5, 15, 2)
        r2 = ops.create_recipe(food.food_id, "Slow cook", 15, 90, 4)
        recipes = ops.get_recipes_by_food(food.food_id)
        assert len(recipes) >= 2
        assert r1 in recipes and r2 in recipes

    def test_search_recipes_by_cooking_time(self, session):
        """Return recipes under max cook time."""
        food = ops.create_food("Bread", "Baked", "url")
        ops.create_recipe(food.food_id, "Quick bake", 5, 20, 2)
        ops.create_recipe(food.food_id, "Long bake", 10, 60, 4)

        fast = ops.search_recipes_by_cooking_time(30)
        assert all(r.cook_time <= 30 for r in fast)

    def test_get_recipes_by_servings(self, session):
        """Return all recipes with a given number of servings."""
        food = ops.create_food("Porridge", "Warm", "url")
        ops.create_recipe(food.food_id, "Simmer oats", 5, 10, 1)
        ops.create_recipe(food.food_id, "Double batch", 5, 10, 2)

        results = ops.get_recipes_by_servings(1)
        assert all(r.servings == 1 for r in results)

    def test_get_low_calorie_recipes(self, session):
        """Return recipes with nutritional calories ≤ max_calories."""
        food = ops.create_food("Bar", "Energy", "url")
        low = ops.create_recipe(food.food_id, "Low cal", 5, 5, 1)
        high = ops.create_recipe(food.food_id, "High cal", 5, 5, 1)

        ops.create_nutritional_info(low.recipe_id, 150, 5, 10, 5)
        ops.create_nutritional_info(high.recipe_id, 500, 10, 50, 20)

        results = ops.get_low_calorie_recipes(200)
        assert low in results
        assert high not in results

    def test_get_all_recipes_with_details(self, session):
        """Return all recipes with food, ingredients, categories, and nutrition."""
        food = ops.create_food("Pizza", "Italian", "url")
        recipe = ops.create_recipe(food.food_id, "Bake at 220C", 15, 20, 2)
        ing = ops.create_ingredient("Cheese", "img")
        cat = ops.create_category("Dinner", "Evening meals")

        ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 100, "g")
        ops.add_category_to_recipe(recipe.recipe_id, cat.category_id)
        ops.create_nutritional_info(recipe.recipe_id, 400, 15, 30, 20)

        results = ops.get_all_recipes_with_details()
        assert isinstance(results, list)
        assert any(r.recipe_id == recipe.recipe_id for r in results)

    def test_get_recipe_full_details_success(self, session):
        """Return full details for a specific recipe."""
        food = ops.create_food("Burger", "Grilled", "url")
        recipe = ops.create_recipe(food.food_id, "Grill and stack", 10, 15, 1)
        ing = ops.create_ingredient("Beef", "img")
        cat = ops.create_category("Lunch", "Noon meals")

        ops.add_ingredient_to_recipe(recipe.recipe_id, ing.ingredient_id, 1, "patty")
        ops.add_category_to_recipe(recipe.recipe_id, cat.category_id)
        ops.create_nutritional_info(recipe.recipe_id, 500, 25, 40, 30)

        result = ops.get_recipe_full_details(recipe.recipe_id)
        assert result.recipe_id == recipe.recipe_id
        assert result.nutritional_info is not None
        assert any(i.name == "Beef" for i in result.ingredients)
        assert any(c.name == "Lunch" for c in result.categories)

    def test_get_recipe_full_details_not_found(self, session):
        """Raise 404 for non-existent recipe."""
        with pytest.raises(NotFound):
            ops.get_recipe_full_details(99999)
