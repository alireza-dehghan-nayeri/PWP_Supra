"""
Pytest Test Suite for the Food Manager API

This module contains fixtures, utility functions, and test cases for verifying
the API endpoints of the Food Manager application. It tests CRUD operations
for resources such as foods, categories, ingredients, recipes, and nutritional
information using Flask's test client.
"""

# pylint: disable=redefined-outer-name,unused-argument,too-many-lines,wrong-import-order,unused-import,import-error

import json
import os
import tempfile

import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers

# Import the application factory and database handle
from food_manager import create_app, db
# Import models if needed (currently not used in tests)
# from food_manager.models import Food, Ingredient, Category

# ------------------------------------------------------------------------------
# Pytest Fixtures
# ------------------------------------------------------------------------------

@pytest.fixture
def client():
    """
    Create a Flask test client using a temporary SQLite database.

    This fixture configures a temporary database to run tests in isolation.
    It creates all tables before tests run and cleans up (drops tables and deletes
    the temporary file) after the tests finish.

    Yields:
        FlaskClient: The test client for the Flask application.
    """
    # Create a temporary file for the database
    db_fd, db_fname = tempfile.mkstemp()
    # Define test configuration using the temporary database file
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname, "TESTING": True}

    # Create the Flask app using the test configuration
    app = create_app(config)

    with app.app_context():
        db.create_all()  # Create all tables

    # Yield the test client for use in tests
    yield app.test_client()

    # Cleanup: remove the session, drop all tables, and delete the temporary file
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_fname)


@pytest.fixture
def setup_food(client):
    """
    Fixture to add a food item to the test database before running tests.

    Args:
        client (FlaskClient): The Flask test client.
    """
    food_data = {
        "name": "Pizza",
        "description": "Cheesy goodness",
        "image_url": "http://example.com/pizza.jpg"
    }
    client.post("/api/foods/", json=food_data)


@pytest.fixture
def setup_category(client):
    """
    Fixture to add a category to the test database before running tests.

    Args:
        client (FlaskClient): The Flask test client.
    """
    category_data = {
        "description": "Traditional Italian cuisine",
        "name": "Italian"
    }
    client.post("/api/categories/", json=category_data)


@pytest.fixture
def setup_ingredient(client):
    """
    Fixture to add an ingredient to the test database before running tests.

    Args:
        client (FlaskClient): The Flask test client.
    """
    ingredient_data = {
        "image_url": "tomato.jpg",
        "name": "Tomato"
    }
    client.post("/api/ingredients/", json=ingredient_data)


@pytest.fixture
def food_fixture(client):
    """
    Fixture to create a food item and return its ID for use in tests.

    Args:
        client (FlaskClient): The Flask test client.

    Returns:
        int: The ID of the created food item.
    """
    food_data = {
        "name": "Pizza",
        "description": "Cheesy goodness",
        "image_url": "http://example.com/pizza.jpg"
    }
    response = client.post("/api/foods/", json=food_data)
    return response.json['food_id']


@pytest.fixture
def category_fixture(client):
    """
    Fixture to create a category and return its ID for use in tests.

    Args:
        client (FlaskClient): The Flask test client.

    Returns:
        int: The ID of the created category.
    """
    category_data = {
        "description": "Traditional Italian cuisine",
        "name": "Italian"
    }
    response = client.post("/api/categories/", json=category_data)
    return response.json['category_id']


@pytest.fixture
def ingredient_fixture(client):
    """
    Fixture to create an ingredient and return its ID for use in tests.

    Args:
        client (FlaskClient): The Flask test client.

    Returns:
        int: The ID of the created ingredient.
    """
    ingredient_data = {
        "image_url": "tomato.jpg",
        "name": "Tomato"
    }
    response = client.post("/api/ingredients/", json=ingredient_data)
    return response.json['ingredient_id']


@pytest.fixture
def setup_recipe(client, food_fixture, ingredient_fixture, category_fixture):
    """
    Fixture to add a recipe associated with a food item, ingredient, and category.

    Args:
        client (FlaskClient): The Flask test client.
        food_fixture (int): The ID of a food item.
        ingredient_fixture (int): The ID of an ingredient.
        category_fixture (int): The ID of a category.

    Returns:
        int: The ID of the created recipe.
    """
    recipe_data = {
        "food_id": food_fixture,  # Use the food ID from the food_fixture
        "instruction": (
            "1. Make dough with flour, water, and yeast\n"
            "2. Spread tomato sauce\n"
            "3. Add fresh mozzarella and basil\n"
            "4. Bake at 450°F for 15 minutes"
        ),
        "prep_time": 30,
        "cook_time": 15,
        "servings": 4,
    }
    response = client.post("/api/recipes/", json=recipe_data)
    # Assert that the recipe was successfully created
    assert response.status_code == 201, f"Failed to create recipe: {response.data}"
    return response.json['recipe_id']


@pytest.fixture
def setup_nutritional_info_item(client, setup_recipe):
    """
    Fixture to add nutritional info for a recipe.

    Args:
        client (FlaskClient): The Flask test client.
        setup_recipe (int): The ID of the recipe.

    Returns:
        int: The ID of the created nutritional info record.
    """
    nutrition = {
        "recipe_id": setup_recipe,
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 5
    }
    response = client.post("/api/nutritional-info/", json=nutrition)
    # Assert that the nutritional info was successfully created
    assert response.status_code == 201, f"Failed to create nutritional info: {response.data}"
    return response.json['nutritional_info_id']

# ------------------------------------------------------------------------------
# Utility Functions for Test Data
# ------------------------------------------------------------------------------

def get_food_json(food_id=None):
    """
    Generate a sample food JSON object for testing.

    Args:
        food_id (int, optional): If provided, it can be included in the JSON.

    Returns:
        dict: A sample food JSON object.
    """
    food = {
        "name": "Chicken Kourma",
        "description": "Delicious Chicken Kourma",
        "image_url": "http://example.com/Kourma.jpg"
    }
    return food


def get_category_json(category_id=None):
    """
    Generate a sample category JSON object for testing.

    Args:
        category_id (int, optional): If provided, it can be included in the JSON.

    Returns:
        dict: A sample category JSON object.
    """
    category = {
        "name": "Test Category",
        "description": "A test category for API testing"
    }
    return category


def get_ingredient_json(ingredient_id=None):
    """
    Generate a sample ingredient JSON object for testing.

    Args:
        ingredient_id (int, optional): If provided, it can be included in the JSON.

    Returns:
        dict: A sample ingredient JSON object.
    """
    ingredient = {
        "name": "Test Ingredient",
        "image_url": "test_ingredient.jpg"
    }
    return ingredient


def get_recipe_json(recipe_id=None, food_id=1):
    """
    Generate a sample recipe JSON object for testing.

    Args:
        recipe_id (int, optional): If provided, it can be included in the JSON.
        food_id (int): The food ID associated with the recipe.

    Returns:
        dict: A sample recipe JSON object.
    """
    recipe = {
        "food_id": food_id,
        "instruction": "1. Test instruction\n2. Another test instruction",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 4
    }
    return recipe


def get_recipe_put_json(recipe_id=None, food_id=1):
    """
    Generate a sample recipe JSON object for updating (PUT requests) in testing.

    Args:
        recipe_id (int, optional): If provided, it can be included in the JSON.
        food_id (int): The food ID associated with the recipe.

    Returns:
        dict: A sample recipe JSON object suitable for PUT requests.
    """
    recipe = {
        "food_id": 1,
        "instruction": (
            "1. Make dough with flour, water, and yeast\n"
            "2. Spread tomato sauce\n"
            "3. Add fresh mozzarella and basil\n"
            "4. Bake at 450°F for 15 minutes"
        ),
        "prep_time": 30,
        "cook_time": 15,
        "servings": 4
    }
    return recipe


def get_nutritional_info_json(nutritional_info_id=None, recipe_id=1):
    """
    Generate a sample nutritional info JSON object for testing.

    Args:
        nutritional_info_id (int, optional): If provided, it can be included in the JSON.
        recipe_id (int): The recipe ID associated with the nutritional info.

    Returns:
        dict: A sample nutritional info JSON object.
    """
    nutrition = {
        "recipe_id": recipe_id,
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 5
    }
    return nutrition


def get_nutritional_info_put_json():
    """
    Generate a sample nutritional info JSON object for updating (PUT requests) in testing.

    Returns:
        dict: A sample nutritional info JSON object suitable for PUT requests.
    """
    nutrition = {
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 5
    }
    return nutrition

# ------------------------------------------------------------------------------
# Test Classes for API Endpoints
# ------------------------------------------------------------------------------

class TestFoodList:
    """
    Test cases for the FoodListResource endpoint.

    This class tests GET and POST operations on the food list endpoint.
    """
    RESOURCE_URL = "/api/foods/"

    def test_get(self, client: FlaskClient):
        """
        Test GET request to retrieve all food items.

        Verifies that the response status is 200 and that the data is a list containing
        expected keys if sample data exists.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        if len(body) > 0:
            assert "name" in body[0]
            assert "food_id" in body[0]

    def test_post(self, client: FlaskClient):
        """
        Test POST request to create a new food item.

        Checks that valid food data creates a new food item, that invalid data types return
        the correct error status, and that missing required fields yield an error.
        """
        # Valid data test
        valid = get_food_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "food_id" in body
        assert body["name"] == valid["name"]

        # Invalid data type test
        resp = client.post(
            self.RESOURCE_URL,
            data={},  # Empty dictionary to simulate an invalid type
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Missing required field test
        invalid = get_food_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        if resp.status_code == 500:
            print("Server Error:", resp.data.decode())
        assert resp.status_code == 500

class TestFoodItem:
    """
    Test cases for the FoodResource endpoint.

    This class tests GET, PUT, and DELETE operations for individual food items.
    """
    RESOURCE_URL = "/api/foods/1/"
    INVALID_URL = "/api/foods/invalid/"

    def test_get(self, client: FlaskClient, setup_food):
        """
        Test GET request to retrieve a specific food item.

        Uses the setup_food fixture to ensure the food exists.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "food_id" in body
        assert body["food_id"] == 1

    def test_put(self, client: FlaskClient, setup_food):
        """
        Test PUT request to update a food item.

        Validates error responses for wrong content type and invalid URLs, and confirms
        that valid data results in a successful update.
        """
        valid = get_food_json()
        # Test with wrong content type
        resp = client.put(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        # Test with invalid URL
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        # Test with valid update
        valid["name"] = "Updated Food Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Food Name"

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove a food item.

        Creates a food item, deletes it, and verifies that subsequent deletion attempts fail.
        """
        food = get_food_json()
        create_resp = client.post("/api/foods/", json=food)
        created_food = json.loads(create_resp.data)
        delete_url = f"/api/foods/{created_food['food_id']}/"
        # Test deletion
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        # Attempt deletion again (should fail)
        resp = client.delete(delete_url)
        assert resp.status_code == 404
        # Test deletion with an invalid URL
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestCategoryList:
    """
    Test cases for the CategoryListResource endpoint.

    This class tests GET and POST operations on the category list endpoint.
    """
    RESOURCE_URL = "/api/categories/"

    def test_get(self, client: FlaskClient):
        """
        Test GET request to retrieve all categories.

        Verifies that the response is a list containing expected keys.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        if len(body) > 0:
            assert "name" in body[0]
            assert "category_id" in body[0]

    def test_post(self, client: FlaskClient):
        """
        Test POST request to create a new category.

        Checks valid creation, error for invalid data types, and error for missing required fields.
        """
        valid = get_category_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "category_id" in body
        assert body["name"] == valid["name"]

        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        invalid = get_category_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500

class TestCategoryItem:
    """
    Test cases for the CategoryResource endpoint.

    This class tests GET, PUT, and DELETE operations for a specific category.
    """
    RESOURCE_URL = "/api/categories/1/"
    INVALID_URL = "/api/categories/invalid/"

    def test_get(self, client: FlaskClient, setup_category):
        """
        Test GET request to retrieve a specific category.

        Validates that the category is returned for a valid ID and that an invalid ID returns a 404.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "category_id" in body
        assert body["category_id"] == 1
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_category):
        """
        Test PUT request to update a category.

        Verifies error responses for incorrect content type and invalid URL,
        and confirms a successful update with valid data.
        """
        valid = get_category_json()
        resp = client.put(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        valid["name"] = "Updated Category Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Category Name"

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove a category.

        Creates a category, then deletes it, ensuring a successful deletion.
        """
        category = get_category_json()
        create_resp = client.post("/api/categories/", json=category)
        created_category = json.loads(create_resp.data)
        delete_url = f"/api/categories/{created_category['category_id']}/"
        resp = client.delete(delete_url)
        assert resp.status_code == 204

class TestIngredientList:
    """
    Test cases for the IngredientListResource endpoint.

    This class tests GET and POST operations for the ingredient list endpoint.
    """
    RESOURCE_URL = "/api/ingredients/"

    def test_get(self, client: FlaskClient):
        """
        Test GET request to retrieve all ingredients.

        Ensures that the response is a list containing the expected keys.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        if len(body) > 0:
            assert "name" in body[0]
            assert "ingredient_id" in body[0]

    def test_post(self, client: FlaskClient):
        """
        Test POST request to create a new ingredient.

        Validates that a new ingredient is created with valid data and that errors
        occur for invalid data types or missing required fields.
        """
        valid = get_ingredient_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "ingredient_id" in body
        assert body["name"] == valid["name"]

        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        invalid = get_ingredient_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500

class TestIngredientItem:
    """
    Test cases for the IngredientResource endpoint.

    This class tests GET, PUT, and DELETE operations for an individual ingredient.
    """
    RESOURCE_URL = "/api/ingredients/1/"
    INVALID_URL = "/api/ingredients/invalid/"

    def test_get(self, client: FlaskClient, setup_ingredient):
        """
        Test GET request to retrieve a specific ingredient.

        Verifies that a valid ingredient is returned and an invalid ID returns 404.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "ingredient_id" in body
        assert body["ingredient_id"] == 1
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_ingredient):
        """
        Test PUT request to update an ingredient.

        Checks error responses for wrong content type and invalid URL, and confirms that
        valid data results in a successful update.
        """
        valid = get_ingredient_json(1)
        resp = client.put(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        valid["name"] = "Updated Ingredient Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Ingredient Name"

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove an ingredient.

        Creates an ingredient, then deletes it, verifying that deletion is successful.
        """
        ingredient = get_ingredient_json()
        create_resp = client.post("/api/ingredients/", json=ingredient)
        created_ingredient = json.loads(create_resp.data)
        delete_url = f"/api/ingredients/{created_ingredient['ingredient_id']}/"
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestRecipeList:
    """
    Test cases for the RecipeListResource endpoint.

    This class tests GET and POST operations for the recipe list endpoint.
    """
    RESOURCE_URL = "/api/recipes/"

    def test_get(self, client: FlaskClient):
        """
        Test GET request to retrieve all recipes.

        Asserts that the response is a list containing expected keys.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        if len(body) > 0:
            assert "recipe_id" in body[0]
            assert "food_id" in body[0]

    def test_post(self, client: FlaskClient):
        """
        Test POST request to create a new recipe.

        Ensures that a recipe is created successfully when valid data is provided,
        and that errors are returned for invalid or incomplete data.
        """
        # Ensure a food item exists first.
        food = get_food_json()
        client.post("/api/foods/", json=food)
        valid = get_recipe_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["food_id"] == valid["food_id"]
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        invalid = get_recipe_json()
        invalid.pop("food_id")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500

class TestRecipeItem:
    """
    Test cases for the RecipeResource endpoint.

    This class tests GET, PUT, and DELETE operations for an individual recipe.
    """
    RESOURCE_URL = "/api/recipes/1/"
    INVALID_URL = "/api/recipes/invalid/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """
        Test GET request to retrieve a specific recipe.

        Uses the recipe ID from the setup_recipe fixture to verify correct retrieval.
        """
        resource_url = f"/api/recipes/{setup_recipe}/"
        resp = client.get(resource_url)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body
        resp = client.get("/api/recipes/invalid/")
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_recipe):
        """
        Test PUT request to update a recipe.

        Verifies error responses for incorrect content types and invalid URLs,
        and confirms that valid updates change the recipe correctly.
        """
        valid = get_recipe_put_json()
        resp = client.put(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        valid["prep_time"] = 25
        valid["cook_time"] = 40
        resp = client.put(self.RESOURCE_URL, json=valid)
        if resp.status_code == 500:
            print("Server Error:", resp.data.decode())
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["prep_time"] == 25
        assert body["cook_time"] == 40

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove a recipe.

        Creates a recipe (after ensuring a food item exists), deletes it,
        and confirms that deletion is successful. Also verifies that deleting an
        already deleted or invalid recipe returns the appropriate error.
        """
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]
        recipe = get_recipe_json(food_id=food_id)
        create_resp = client.post("/api/recipes/", json=recipe)
        created_recipe = json.loads(create_resp.data)
        delete_url = f"/api/recipes/{created_recipe['recipe_id']}/"
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404

class TestRecipeIngredient:
    """
    Test cases for the RecipeIngredientResource endpoint.

    This class tests GET, POST, PUT, and DELETE operations for managing
    ingredients associated with a recipe.
    """
    RESOURCE_URL = "/api/recipes/1/ingredients/"
    INVALID_URL = "/api/recipes/invalid/ingredients/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """
        Test GET request to retrieve ingredients for a recipe.

        Checks that the correct recipe ID is returned and that an invalid ID returns 404.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["recipe_id"] == 1
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client: FlaskClient):
        """
        Test POST request to add an ingredient to a recipe.

        Verifies that a valid ingredient is added successfully and that errors are
        raised for invalid data types, missing required fields, or non-existent recipes.
        """
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        valid = {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "cups"
        }
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "message" in body
        assert body["recipe_id"] == 1
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        invalid = {"ingredient_id": ingredient_id}  # Missing quantity.
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient):
        """
        Test PUT request to update a recipe ingredient.

        First adds an ingredient to a recipe, then updates its quantity and unit.
        Verifies proper error responses for missing ingredient_id or invalid recipe IDs.
        """
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        add_data = {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "cups"
        }
        client.post(self.RESOURCE_URL, json=add_data)
        update_data = {
            "ingredient_id": ingredient_id,
            "quantity": 3,
            "unit": "tablespoons"
        }
        resp = client.put(self.RESOURCE_URL, json=update_data)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "message" in body
        assert body["recipe_id"] == 1
        invalid = {"quantity": 4, "unit": "teaspoons"}
        resp = client.put(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        resp = client.put(self.INVALID_URL, json=update_data)
        assert resp.status_code == 404

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove an ingredient from a recipe.

        Adds an ingredient to a recipe, then deletes it and confirms successful deletion.
        Also checks for error responses when required fields are missing or using an invalid recipe.
        """
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        add_data = {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "cups"
        }
        client.post(self.RESOURCE_URL, json=add_data)
        delete_data = {"ingredient_id": ingredient_id}
        resp = client.delete(self.RESOURCE_URL, json=delete_data)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "message" in body
        invalid = {}
        resp = client.delete(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        resp = client.delete(self.INVALID_URL, json=delete_data)
        assert resp.status_code == 404

class TestRecipeCategory:
    """
    Test cases for the RecipeCategoryResource endpoint.

    This class tests GET, POST, and DELETE operations for managing
    categories associated with a recipe.
    """
    RESOURCE_URL = "/api/recipes/1/categories/"
    INVALID_URL = "/api/recipes/invalid/categories/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """
        Test GET request to retrieve categories for a recipe.

        Verifies that the correct recipe ID is returned and that an invalid ID returns 404.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["recipe_id"] == 1
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client: FlaskClient):
        """
        Test POST request to add a category to a recipe.

        Ensures that valid category data is added successfully and that error responses are
        returned for invalid input or non-existent recipes.
        """
        category = get_category_json()
        category_resp = client.post("/api/categories/", json=category)
        category_id = json.loads(category_resp.data)["category_id"]
        valid = {"category_id": category_id}
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "message" in body
        assert body["recipe_id"] == 1
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        invalid = {}  # Missing category_id.
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove a category from a recipe.

        Verifies that deletion is successful for a valid category and that errors
        occur for missing fields or invalid recipes.
        """
        category = get_category_json()
        category_resp = client.post("/api/categories/", json=category)
        category_id = json.loads(category_resp.data)["category_id"]
        add_data = {"category_id": category_id}
        client.post(self.RESOURCE_URL, json=add_data)
        delete_data = {"category_id": category_id}
        resp = client.delete(self.RESOURCE_URL, json=delete_data)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "message" in body
        invalid = {}
        resp = client.delete(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        resp = client.delete(self.INVALID_URL, json=delete_data)
        assert resp.status_code == 404

class TestNutritionalInfoList:
    """
    Test cases for the NutritionalInfoListResource endpoint.

    This class tests GET and POST operations for nutritional information.
    """
    RESOURCE_URL = "/api/nutritional-info/"

    def test_get(self, client: FlaskClient):
        """
        Test GET request to retrieve all nutritional info records.

        Checks that the response is a list and that, if data exists, expected keys are present.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        if len(body) > 0:
            assert "nutritional_info_id" in body[0]
            assert "recipe_id" in body[0]

    def test_post(self, client: FlaskClient):
        """
        Test POST request to create new nutritional info.

        Ensures that a food item and recipe exist before creating nutritional info.
        Also checks error responses for invalid data.
        """
        # Create food item
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]

        # Create recipe item
        recipe = get_recipe_json(food_id=food_id)
        recipe_resp = client.post("/api/recipes/", json=recipe)
        recipe_id = json.loads(recipe_resp.data)["recipe_id"]

        valid = get_nutritional_info_json(recipe_id=recipe_id)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "nutritional_info_id" in body
        assert body["calories"] == valid["calories"]

        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        invalid = get_nutritional_info_json()
        invalid.pop("calories")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500

class TestNutritionalInfoItem:
    """
    Test cases for the NutritionalInfoResource endpoint.

    This class tests GET, PUT, and DELETE operations for a specific nutritional info record.
    """
    RESOURCE_URL = "/api/nutritional-info/1/"
    INVALID_URL = "/api/nutritional-info/invalid/"

    def test_get(self, client: FlaskClient, setup_nutritional_info_item):
        """
        Test GET request to retrieve specific nutritional info.

        Asserts that a valid nutritional info record is returned and that an invalid ID returns 404.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "nutritional_info_id" in body
        assert body["nutritional_info_id"] == 1
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_nutritional_info_item):
        """
        Test PUT request to update nutritional info.

        Verifies that errors are returned for invalid content types and URLs,
        and confirms that valid updates modify the record.
        """
        valid = get_nutritional_info_put_json()
        resp = client.put(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)
        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404
        valid["calories"] = 300
        valid["protein"] = 15
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["calories"] == 300
        assert body["protein"] == 15

    def test_delete(self, client: FlaskClient):
        """
        Test DELETE request to remove nutritional info.

        Creates a nutritional info record (after ensuring that a food and recipe exist),
        then deletes it and verifies the deletion.
        """
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]

        recipe = get_recipe_json(food_id=food_id)
        recipe_resp = client.post("/api/recipes/", json=recipe)
        recipe_id = json.loads(recipe_resp.data)["recipe_id"]

        nutrition = get_nutritional_info_json(recipe_id=recipe_id)
        create_resp = client.post("/api/nutritional-info/", json=nutrition)
        assert create_resp.status_code == 201
        nutrition_id = json.loads(create_resp.data)["nutritional_info_id"]

        delete_resp = client.delete(f"/api/nutritional-info/{nutrition_id}/")
        assert delete_resp.status_code == 204
