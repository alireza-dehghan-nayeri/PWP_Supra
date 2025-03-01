import json
import pytest
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.datastructures import Headers
from jsonschema import validate, ValidationError
import tempfile, os

from food_manager import create_app, db
from food_manager.models import Food, Ingredient, Category
from food_manager.db_operations import *

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {"SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname, "TESTING": True}

    app = create_app(config)

    with app.app_context():
        db.create_all()

    yield app.test_client()

    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()
    # with app.app_context():
    
    os.close(db_fd)
    os.unlink(db_fname)
                                                                                       
@pytest.fixture
def setup_food(client):
    """Setup: Add a food item before running tests."""
    food_data = {"name": "Pizza", "description": "Cheesy goodness", "image_url": "http://example.com/pizza.jpg"}
    client.post("/api/foods/", json=food_data)
    
@pytest.fixture
def setup_category(client):
    """Setup: Add a food item before running tests."""
    category_data = {"description": "Traditional Italian cuisine", "name": "Italian"}
    client.post("/api/categories/", json=category_data)
    
@pytest.fixture
def setup_ingredient(client):
    """Setup: Add a food item before running tests."""
    ingredient_data = {"image_url": "tomato.jpg", "name": "Tomato"}
    client.post("/api/ingredients/", json=ingredient_data)
    
@pytest.fixture
def food_fixture(client):
    """Setup: Add a food item before running tests."""
    food_data = {
        "name": "Pizza",
        "description": "Cheesy goodness",
        "image_url": "http://example.com/pizza.jpg"
    }
    response = client.post("/api/foods/", json=food_data)
    return response.json['food_id']  # Return the food ID


@pytest.fixture
def category_fixture(client):
    """Setup: Add a category before running tests."""
    category_data = {
        "description": "Traditional Italian cuisine",
        "name": "Italian"
    }
    response = client.post("/api/categories/", json=category_data)
    return response.json['category_id']  # Return the category ID


@pytest.fixture
def ingredient_fixture(client):
    """Setup: Add an ingredient before running tests."""
    ingredient_data = {
        "image_url": "tomato.jpg",
        "name": "Tomato"
    }
    response = client.post("/api/ingredients/", json=ingredient_data)
    return response.json['ingredient_id']  # Return the ingredient ID

@pytest.fixture
def setup_recipe(client, food_fixture, ingredient_fixture, category_fixture):
    """Setup: Add a recipe related to the food item before running tests."""
    recipe_data = {
        'food_id': food_fixture,  # Use the food ID created in the food_fixture
        'instruction': ('1. Make dough with flour, water, and yeast\n'
                        '2. Spread tomato sauce\n'
                        '3. Add fresh mozzarella and basil\n'
                        '4. Bake at 450°F for 15 minutes'),
        'prep_time': 30,
        'cook_time': 15,
        'servings': 4,
    }
    response = client.post("/api/recipes/", json=recipe_data)
    
    # Assert that the recipe was successfully created
    assert response.status_code == 201, f"Failed to create recipe: {response.data}"
    
    # Return the recipe ID from the response
    return response.json['recipe_id']

@pytest.fixture
def setup_nutritional_info_item(client, setup_recipe):
    """Setup: Add a recipe related to the food item before running tests."""
    nutrition = {
        "recipe_id": setup_recipe,
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 5
    }
    response = client.post("/api/nutritional-info/", json=nutrition)
    
    # Assert that the recipe was successfully created
    assert response.status_code == 201, f"Failed to create recipe: {response.data}"
    
    # Return the recipe ID from the response
    return response.json['nutritional_info_id']

# Utility functions to get test data
def get_food_json(food_id=None):
    """
    Return a sample food JSON object for testing.
    If food_id is provided, it will be included in the returned JSON.
    """
    food = {
        "name": "Chicken Kourma",
        "description": "Delicious Chicken Kourma",
        "image_url": "http://example.com/Kourma.jpg"
    }
    return food

def get_category_json(category_id=None):
    """
    Return a sample category JSON object for testing.
    If category_id is provided, it will be included in the returned JSON.
    """
    category = {
        "name": "Test Category",
        "description": "A test category for API testing"
    }
    return category

def get_ingredient_json(ingredient_id=None):
    """
    Return a sample ingredient JSON object for testing.
    If ingredient_id is provided, it will be included in the returned JSON.
    """
    ingredient = {
        "name": "Test Ingredient",
        "image_url": "test_ingredient.jpg"
    }
    return ingredient

def get_recipe_json(recipe_id=None, food_id=1):
    """
    Return a sample recipe JSON object for testing.
    If recipe_id is provided, it will be included in the returned JSON.
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
    Return a sample recipe JSON object for testing.
    If recipe_id is provided, it will be included in the returned JSON.
    """
    recipe = {'food_id': 1, 'instruction': '1. Make dough with flour, water, and yeast\n2. Spread tomato sauce\n3. Add fresh mozzarella and basil\n4. Bake at 450°F for 15 minutes', 'prep_time': 30, 'cook_time': 15, 'servings': 4}
    
    return recipe

def get_nutritional_info_json(nutritional_info_id=None, recipe_id=1):
    """
    Return a sample nutritional info JSON object for testing.
    If nutritional_info_id is provided, it will be included in the returned JSON.
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
    Return a sample nutritional info JSON object for testing.
    If nutritional_info_id is provided, it will be included in the returned JSON.
    """
    nutrition = {
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 5
    }
    return nutrition


class TestFoodList:
    """Test cases for the FoodListResource endpoint."""
    RESOURCE_URL = "/api/foods/"

    def test_get(self, client: FlaskClient):
        """Test GET request to retrieve all foods."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        # Check if sample data exists
        if len(body) > 0:
            assert "name" in body[0]
            assert "food_id" in body[0]

    def test_post(self, client: FlaskClient):
        """Test POST request to create a new food item."""
        # Test with valid data
        valid = get_food_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "food_id" in body
        assert body["name"] == valid["name"]

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data={
},
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = get_food_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        
        # Print response body to debug 500 errors
        if resp.status_code == 500:
            print("Server Error:", resp.data.decode())

        assert resp.status_code == 500

class TestFoodItem:
    """Test cases for the FoodResource endpoint."""
    RESOURCE_URL = "/api/foods/1/"
    INVALID_URL = "/api/foods/invalid/"

    def test_get(self, client: FlaskClient, setup_food):
        """Test GET request to retrieve a specific food item."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "food_id" in body
        assert body["food_id"] == 1


    def test_put(self, client: FlaskClient, setup_food):
        """Test PUT request to update a food item."""
        # Get valid food data
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
        
        # Test with valid data
        # valid["food_id"] = 1
        valid["name"] = "Updated Food Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Food Name"

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove a food item."""
        # Create a food to delete
        food = get_food_json()
        create_resp = client.post("/api/foods/", json=food)
        created_food = json.loads(create_resp.data)
        delete_url = f"/api/foods/{created_food['food_id']}/"
        
        # Test deleting the food
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        
        # Test deleting the same food again (should fail)
        resp = client.delete(delete_url)
        assert resp.status_code == 404
        
        # Test with invalid URL
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestCategoryList:
    """Test cases for the CategoryListResource endpoint."""
    RESOURCE_URL = "/api/categories/"

    def test_get(self, client: FlaskClient):
        """Test GET request to retrieve all categories."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        # Check if sample data exists
        if len(body) > 0:
            assert "name" in body[0]
            assert "category_id" in body[0]

    def test_post(self, client: FlaskClient):
        """Test POST request to create a new category."""
        # Test with valid data
        valid = get_category_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "category_id" in body
        assert body["name"] == valid["name"]

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = get_category_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500


class TestCategoryItem:
    """Test cases for the CategoryResource endpoint."""
    RESOURCE_URL = "/api/categories/1/"
    INVALID_URL = "/api/categories/invalid/"

    def test_get(self, client: FlaskClient, setup_category):
        """Test GET request to retrieve a specific category."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "category_id" in body
        assert body["category_id"] == 1

        # Test with invalid ID
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_category):
        """Test PUT request to update a category."""
        # Get valid category data
        valid = get_category_json()
        
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
        
        # Test with valid data
        valid["name"] = "Updated Category Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Category Name"

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove a category."""
        # Create a category to delete
        category = get_category_json()
        create_resp = client.post("/api/categories/", json=category)
        created_category = json.loads(create_resp.data)
        delete_url = f"/api/categories/{created_category['category_id']}/"
        
        # Test deleting the category
        resp = client.delete(delete_url)
        assert resp.status_code == 204


class TestIngredientList:
    """Test cases for the IngredientListResource endpoint."""
    RESOURCE_URL = "/api/ingredients/"

    def test_get(self, client: FlaskClient):
        """Test GET request to retrieve all ingredients."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        # Check if sample data exists
        if len(body) > 0:
            assert "name" in body[0]
            assert "ingredient_id" in body[0]

    def test_post(self, client: FlaskClient):
        """Test POST request to create a new ingredient."""
        # Test with valid data
        valid = get_ingredient_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "ingredient_id" in body
        assert body["name"] == valid["name"]

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = get_ingredient_json()
        invalid.pop("name")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500


class TestIngredientItem:
    """Test cases for the IngredientResource endpoint."""
    RESOURCE_URL = "/api/ingredients/1/"
    INVALID_URL = "/api/ingredients/invalid/"

    def test_get(self, client: FlaskClient, setup_ingredient):
        """Test GET request to retrieve a specific ingredient."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "ingredient_id" in body
        assert body["ingredient_id"] == 1

        # Test with invalid ID
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_ingredient):
        """Test PUT request to update an ingredient."""
        # Get valid ingredient data
        valid = get_ingredient_json(1)
        
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
        
        # Test with valid data
        valid["name"] = "Updated Ingredient Name"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["name"] == "Updated Ingredient Name"

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove an ingredient."""
        # Create an ingredient to delete
        ingredient = get_ingredient_json()
        create_resp = client.post("/api/ingredients/", json=ingredient)
        created_ingredient = json.loads(create_resp.data)
        delete_url = f"/api/ingredients/{created_ingredient['ingredient_id']}/"
        
        # Test deleting the ingredient
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        
        # Test with invalid URL
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestRecipeList:
    """Test cases for the RecipeListResource endpoint."""
    RESOURCE_URL = "/api/recipes/"

    def test_get(self, client: FlaskClient):
        """Test GET request to retrieve all recipes."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        # Check if sample data exists
        if len(body) > 0:
            assert "recipe_id" in body[0]
            assert "food_id" in body[0]

    def test_post(self, client: FlaskClient):
        """Test POST request to create a new recipe."""
        # Ensure food exists first
        food = get_food_json()
        client.post("/api/foods/", json=food)
        
        # Test with valid data
        valid = get_recipe_json()
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["food_id"] == valid["food_id"]

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = get_recipe_json()
        invalid.pop("food_id")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500


class TestRecipeItem:
    """Test cases for the RecipeResource endpoint."""
    RESOURCE_URL = "/api/recipes/1/"
    INVALID_URL = "/api/recipes/invalid/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """Test GET request to retrieve a specific recipe."""
        # Use the recipe_id returned by the setup_recipe fixture
        resource_url = f"/api/recipes/{setup_recipe}/"  # Dynamically use the recipe_id
        resp = client.get(resource_url)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body  # Check if the returned recipe ID matches the one from the fixture

        # Test with invalid ID
        resp = client.get("/api/recipes/invalid/")
        assert resp.status_code == 404
        
    def test_put(self, client: FlaskClient, setup_recipe):
        """Test PUT request to update a recipe."""
        # Get valid recipe data
        valid = get_recipe_put_json()
        
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
        
        # Test with valid data
        valid["prep_time"] = 25
        valid["cook_time"] = 40
        resp = client.put(self.RESOURCE_URL, json=valid)
        # Print response body to debug 500 errors
        if resp.status_code == 500:
            print("Server Error:", resp.data.decode())
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["prep_time"] == 25
        assert body["cook_time"] == 40
        

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove a recipe."""
        # Create a recipe to delete
        # First ensure food exists
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]
        
        # Then create recipe
        recipe = get_recipe_json(food_id=food_id)
        create_resp = client.post("/api/recipes/", json=recipe)
        created_recipe = json.loads(create_resp.data)
        delete_url = f"/api/recipes/{created_recipe['recipe_id']}/"
        
        # Test deleting the recipe
        resp = client.delete(delete_url)
        assert resp.status_code == 204
        
        # Test with invalid URL
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


class TestRecipeIngredient:
    """Test cases for the RecipeIngredientResource endpoint."""
    RESOURCE_URL = "/api/recipes/1/ingredients/"
    INVALID_URL = "/api/recipes/invalid/ingredients/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """Test GET request to retrieve recipe ingredients."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["recipe_id"] == 1

        # Test with invalid ID
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client: FlaskClient):
        """Test POST request to add an ingredient to a recipe."""
        # Create a new ingredient if needed
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        
        # Test with valid data
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

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = {"ingredient_id": ingredient_id}  # Missing quantity
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400

        # Test with non-existent recipe
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient):
        """Test PUT request to update a recipe ingredient."""
        # First add an ingredient to update
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        
        add_data = {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "cups"
        }
        client.post(self.RESOURCE_URL, json=add_data)
        
        # Test with valid update
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

        # Test with missing ingredient_id
        invalid = {"quantity": 4, "unit": "teaspoons"}
        resp = client.put(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400

        # Test with non-existent recipe
        resp = client.put(self.INVALID_URL, json=update_data)
        assert resp.status_code == 404

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove an ingredient from a recipe."""
        # First add an ingredient to delete
        ingredient = get_ingredient_json()
        ingredient_resp = client.post("/api/ingredients/", json=ingredient)
        ingredient_id = json.loads(ingredient_resp.data)["ingredient_id"]
        
        add_data = {
            "ingredient_id": ingredient_id,
            "quantity": 2,
            "unit": "cups"
        }
        client.post(self.RESOURCE_URL, json=add_data)
        
        # Test with valid delete
        delete_data = {"ingredient_id": ingredient_id}
        resp = client.delete(self.RESOURCE_URL, json=delete_data)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "message" in body
        
        # Test with missing ingredient_id
        invalid = {}
        resp = client.delete(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        
        # Test with non-existent recipe
        resp = client.delete(self.INVALID_URL, json=delete_data)
        assert resp.status_code == 404


class TestRecipeCategory:
    """Test cases for the RecipeCategoryResource endpoint."""
    RESOURCE_URL = "/api/recipes/1/categories/"
    INVALID_URL = "/api/recipes/invalid/categories/"

    def test_get(self, client: FlaskClient, setup_recipe):
        """Test GET request to retrieve recipe categories."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "recipe_id" in body
        assert body["recipe_id"] == 1

        # Test with invalid ID
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_post(self, client: FlaskClient):
        """Test POST request to add a category to a recipe."""
        # Create a new category if needed
        category = get_category_json()
        category_resp = client.post("/api/categories/", json=category)
        category_id = json.loads(category_resp.data)["category_id"]
        
        # Test with valid data
        valid = {"category_id": category_id}
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "message" in body
        assert body["recipe_id"] == 1

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = {}  # Missing category_id
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400

        # Test with non-existent recipe
        resp = client.post(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove a category from a recipe."""
        # First add a category to delete
        category = get_category_json()
        category_resp = client.post("/api/categories/", json=category)
        category_id = json.loads(category_resp.data)["category_id"]
        
        add_data = {"category_id": category_id}
        client.post(self.RESOURCE_URL, json=add_data)
        
        # Test with valid delete
        delete_data = {"category_id": category_id}
        resp = client.delete(self.RESOURCE_URL, json=delete_data)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "message" in body
        
        # Test with missing category_id
        invalid = {}
        resp = client.delete(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 400
        
        # Test with non-existent recipe
        resp = client.delete(self.INVALID_URL, json=delete_data)
        assert resp.status_code == 404


class TestNutritionalInfoList:
    """Test cases for the NutritionalInfoListResource endpoint."""
    RESOURCE_URL = "/api/nutritional-info/"

    def test_get(self, client: FlaskClient):
        """Test GET request to retrieve all nutritional info records."""
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert isinstance(body, list)
        # Check if sample data exists
        if len(body) > 0:
            assert "nutritional_info_id" in body[0]
            assert "recipe_id" in body[0]

    def test_post(self, client: FlaskClient):
        """Test POST request to create new nutritional info."""
        # Ensure recipe exists first
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]
        
        recipe = get_recipe_json(food_id=food_id)
        recipe_resp = client.post("/api/recipes/", json=recipe)
        recipe_id = json.loads(recipe_resp.data)["recipe_id"]
        
        # Test with valid data
        valid = get_nutritional_info_json(recipe_id=recipe_id)
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        body = json.loads(resp.data)
        assert "nutritional_info_id" in body
        assert body["calories"] == valid["calories"]

        # Test with invalid data type
        resp = client.post(
            self.RESOURCE_URL,
            data="notjson",
            headers=Headers({"Content-Type": "application/json"})
        )
        assert resp.status_code in (400, 415)

        # Test with missing required field
        invalid = get_nutritional_info_json()
        invalid.pop("calories")
        resp = client.post(self.RESOURCE_URL, json=invalid)
        assert resp.status_code == 500


class TestNutritionalInfoItem:
    """Test cases for the NutritionalInfoResource endpoint."""
    RESOURCE_URL = "/api/nutritional-info/1/"
    INVALID_URL = "/api/nutritional-info/invalid/"

    def test_get(self, client: FlaskClient, setup_nutritional_info_item):
        """Test GET request to retrieve specific nutritional info."""
        # Test with valid ID
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert "nutritional_info_id" in body
        assert body["nutritional_info_id"] == 1

        # Test with invalid ID
        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client: FlaskClient, setup_nutritional_info_item):
        """Test PUT request to update nutritional info."""
        # Get valid nutritional info data
        valid = get_nutritional_info_put_json()
        
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
        
        # Test with valid data
        valid["calories"] = 300
        valid["protein"] = 15
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["calories"] == 300
        assert body["protein"] == 15

    def test_delete(self, client: FlaskClient):
        """Test DELETE request to remove nutritional info."""
        # Create nutritional info to delete
        # First ensure recipe exists
        food = get_food_json()
        food_resp = client.post("/api/foods/", json=food)
        food_id = json.loads(food_resp.data)["food_id"]
        
        recipe = get_recipe_json(food_id=food_id)
        recipe_resp = client.post("/api/recipes/", json=recipe)
        recipe_id = json.loads(recipe_resp.data)["recipe_id"]
        
        # Then create nutritional info
        nutrition = get_nutritional_info_json(recipe_id=recipe_id)
        create_resp = client.post("/api/nutritional-info/", json=nutrition)
        
        # Verify creation was successful
        assert create_resp.status_code == 201
        nutrition_id = json.loads(create_resp.data)["nutritional_info_id"]
        
        # Now try to delete it
        delete_resp = client.delete(f"/api/nutritional-info/{nutrition_id}/")
        assert delete_resp.status_code == 204