"""Food Manager Database Operations Module

This module defines various operations for managing food, recipes, ingredients,
categories, and nutritional information in the database.
"""

from food_manager import db

###############################################################################
# Food Operations
###############################################################################

def create_food(name, description=None, image_url=None):
    """
    Create a new food item in the database.

    :param name: The name of the food item.
    :param description: An optional description of the food item.
    :param image_url: An optional URL to an image of the food item.
    :return: The created Food object.
    :raises ValueError: If a food item with the same name already exists.
    """
    
    from food_manager.models import Food
    # Check if a food with the given name already exists.
    existing_food = Food.query.filter_by(name=name).first()
    if existing_food:
        raise ValueError(f"Food with name '{name}' already exists.")

    # Create a new Food object and add it to the session.
    food = Food(name=name, description=description, image_url=image_url)
    db.session.add(food)
    db.session.commit()
    return food


def get_food_by_id(food_id):
    """
    Retrieve a food item by its ID.

    :param food_id: The ID of the food item to retrieve.
    :return: The Food object with the given ID or a 404 error if not found.
    """
    from food_manager.models import Food
    return Food.query.get_or_404(food_id)


def get_all_foods():
    """
    Retrieve all food items from the database.

    :return: A list of all Food objects.
    """
    from food_manager.models import Food
    return Food.query.all()


def update_food(food_id, name=None, description=None, image_url=None):
    """
    Update an existing food item.

    :param food_id: The ID of the food item to update.
    :param name: The new name for the food item (optional).
    :param description: The new description for the food item (optional).
    :param image_url: The new image URL for the food item (optional).
    :return: The updated Food object.
    """
    from food_manager.models import Food
    food = Food.query.get_or_404(food_id)
    if name:
        food.name = name
    if description is not None:
        food.description = description
    if image_url is not None:
        food.image_url = image_url
    db.session.commit()
    return food


def delete_food(food_id):
    """
    Delete a food item from the database.

    :param food_id: The ID of the food item to delete.
    """
    from food_manager.models import Food
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()


###############################################################################
# Recipe Operations
###############################################################################

def create_recipe(food_id, instruction, prep_time, cook_time, servings):
    """
    Create a new recipe in the database.

    :param food_id: The ID of the food item associated with the recipe.
    :param instruction: Cooking instructions for the recipe.
    :param prep_time: Preparation time (in minutes).
    :param cook_time: Cooking time (in minutes).
    :param servings: Number of servings.
    :return: The created Recipe object.
    """
    from food_manager.models import Recipe
    recipe = Recipe(
        food_id=food_id,
        instruction=instruction,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe


def get_recipe_by_id(recipe_id):
    """
    Retrieve a recipe by its ID.

    :param recipe_id: The ID of the recipe to retrieve.
    :return: The Recipe object with the given ID or a 404 error if not found.
    """
    from food_manager.models import Recipe
    return Recipe.query.get_or_404(recipe_id)


def get_all_recipes():
    """
    Retrieve all recipes from the database.

    :return: A list of all Recipe objects.
    """
    from food_manager.models import Recipe
    return Recipe.query.all()


def update_recipe(recipe_id, food_id=None, instruction=None, prep_time=None, cook_time=None,
                  servings=None):
    """
    Update an existing recipe.

    :param recipe_id: The ID of the recipe to update.
    :param food_id: The new food ID (optional).
    :param instruction: The new instruction (optional).
    :param prep_time: The new preparation time (optional).
    :param cook_time: The new cooking time (optional).
    :param servings: The new number of servings (optional).
    :return: The updated Recipe object.
    """
    from food_manager.models import Recipe
    recipe = Recipe.query.get_or_404(recipe_id)
    if food_id is not None:
        recipe.food_id = food_id
    if instruction:
        recipe.instruction = instruction
    if prep_time is not None:
        recipe.prep_time = prep_time
    if cook_time is not None:
        recipe.cook_time = cook_time
    if servings is not None:
        recipe.servings = servings
    db.session.commit()
    return recipe


def delete_recipe(recipe_id):
    """
    Delete a recipe from the database.

    :param recipe_id: The ID of the recipe to delete.
    """
    from food_manager.models import Recipe
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()


###############################################################################
# Ingredient Operations
###############################################################################

def create_ingredient(name, image_url=None):
    """
    Create a new ingredient in the database.

    :param name: The name of the ingredient.
    :param image_url: An optional image URL for the ingredient.
    :return: The created Ingredient object.
    """
    from food_manager.models import Ingredient
    ingredient = Ingredient(name=name, image_url=image_url)
    db.session.add(ingredient)
    db.session.commit()
    return ingredient


def get_ingredient_by_id(ingredient_id):
    """
    Retrieve an ingredient by its ID.

    :param ingredient_id: The ID of the ingredient to retrieve.
    :return: The Ingredient object with the given ID or a 404 error if not found.
    """
    from food_manager.models import Ingredient
    return Ingredient.query.get_or_404(ingredient_id)


def get_all_ingredients():
    """
    Retrieve all ingredients from the database.

    :return: A list of all Ingredient objects.
    """
    from food_manager.models import Ingredient
    return Ingredient.query.all()


def update_ingredient(ingredient_id, name=None, image_url=None):
    """
    Update an existing ingredient.

    :param ingredient_id: The ID of the ingredient to update.
    :param name: The new name for the ingredient (optional).
    :param image_url: The new image URL for the ingredient (optional).
    :return: The updated Ingredient object.
    """
    from food_manager.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    if name:
        ingredient.name = name
    if image_url is not None:
        ingredient.image_url = image_url
    db.session.commit()
    return ingredient


def delete_ingredient(ingredient_id):
    """
    Delete an ingredient from the database.

    :param ingredient_id: The ID of the ingredient to delete.
    """
    from food_manager.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()


###############################################################################
# Category Operations
###############################################################################

def create_category(name, description=None):
    """
    Create a new category in the database.

    :param name: The name of the category.
    :param description: An optional description of the category.
    :return: The created Category object.
    """
    from food_manager.models import Category
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return category


def get_category_by_id(category_id):
    """
    Retrieve a category by its ID.

    :param category_id: The ID of the category to retrieve.
    :return: The Category object with the given ID or a 404 error if not found.
    """
    from food_manager.models import Category
    return Category.query.get_or_404(category_id)


def get_all_categories():
    """
    Retrieve all categories from the database.

    :return: A list of all Category objects.
    """
    from food_manager.models import Category
    return Category.query.all()


def update_category(category_id, name=None, description=None):
    """
    Update an existing category.

    :param category_id: The ID of the category to update.
    :param name: The new name for the category (optional).
    :param description: The new description for the category (optional).
    :return: The updated Category object.
    """
    from food_manager.models import Category
    category = Category.query.get_or_404(category_id)
    if name:
        category.name = name
    if description is not None:
        category.description = description
    db.session.commit()
    return category


def delete_category(category_id):
    """
    Delete a category from the database.

    :param category_id: The ID of the category to delete.
    """
    from food_manager.models import Category
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()


###############################################################################
# Nutritional Info Operations
###############################################################################

def create_nutritional_info(recipe_id, calories, protein, carbs, fat):
    """
    Create a new nutritional information record for a recipe.

    :param recipe_id: The ID of the associated recipe.
    :param calories: Number of calories.
    :param protein: Amount of protein.
    :param carbs: Amount of carbohydrates.
    :param fat: Amount of fat.
    :return: The created NutritionalInfo object.
    """
    from food_manager.models import NutritionalInfo
    nutritional_info = NutritionalInfo(
        recipe_id=recipe_id,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat
    )
    db.session.add(nutritional_info)
    db.session.commit()
    return nutritional_info


def get_all_nutritions():
    """
    Retrieve all nutritional information records from the database.

    :return: A list of all NutritionalInfo objects.
    """
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.all()


def get_nutritional_info_by_id(nutritional_info_id):
    """
    Retrieve a nutritional information record by its ID.

    :param nutritional_info_id: The ID of the nutritional info record.
    :return: The NutritionalInfo object with the given ID or a 404 error if not found.
    """
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.get_or_404(nutritional_info_id)


def get_recipe_nutritional_info(recipe_id):
    """
    Retrieve the nutritional information record for a specific recipe.

    :param recipe_id: The ID of the recipe.
    :return: The NutritionalInfo object for the recipe or a 404 error if not found.
    """
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.filter_by(recipe_id=recipe_id).first_or_404()


def update_nutritional_info(nutritional_info_id, calories=None, protein=None, carbs=None, fat=None):
    """
    Update an existing nutritional information record.

    :param nutritional_info_id: The ID of the nutritional info record to update.
    :param calories: New calorie value (optional).
    :param protein: New protein value (optional).
    :param carbs: New carbohydrate value (optional).
    :param fat: New fat value (optional).
    :return: The updated NutritionalInfo object.
    """
    from food_manager.models import NutritionalInfo
    nutritional_info = NutritionalInfo.query.get_or_404(nutritional_info_id)
    if calories is not None:
        nutritional_info.calories = calories
    if protein is not None:
        nutritional_info.protein = protein
    if carbs is not None:
        nutritional_info.carbs = carbs
    if fat is not None:
        nutritional_info.fat = fat
    db.session.commit()
    return nutritional_info


def delete_nutritional_info(nutritional_info_id):
    """
    Delete a nutritional information record from the database.

    :param nutritional_info_id: The ID of the nutritional info record to delete.
    """
    from food_manager.models import NutritionalInfo
    nutritional_info = NutritionalInfo.query.get_or_404(nutritional_info_id)
    db.session.delete(nutritional_info)
    db.session.commit()


###############################################################################
# Recipe-Ingredient Operations
###############################################################################

def add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit='piece'):
    """
    Associate an ingredient with a recipe with a specified quantity and unit.

    :param recipe_id: The ID of the recipe.
    :param ingredient_id: The ID of the ingredient.
    :param quantity: The quantity of the ingredient.
    :param unit: The unit of measurement (default is 'piece').
    :return: The created RecipeIngredient association object.
    """
    from food_manager.models import RecipeIngredient
    recipe_ingredient = RecipeIngredient(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id,
        quantity=quantity,
        unit=unit
    )
    db.session.add(recipe_ingredient)
    db.session.commit()
    return recipe_ingredient


def update_recipe_ingredient(recipe_id, ingredient_id, quantity=None, unit=None):
    """
    Update the quantity and/or unit of an ingredient associated with a recipe.

    :param recipe_id: The ID of the recipe.
    :param ingredient_id: The ID of the ingredient.
    :param quantity: The new quantity (optional).
    :param unit: The new unit (optional).
    :return: The updated RecipeIngredient association object.
    """
    from food_manager.models import RecipeIngredient
    recipe_ingredient = RecipeIngredient.query.filter_by(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id
    ).first_or_404()
    if quantity is not None:
        recipe_ingredient.quantity = quantity
    if unit is not None:
        recipe_ingredient.unit = unit
    db.session.commit()
    return recipe_ingredient


def remove_ingredient_from_recipe(recipe_id, ingredient_id):
    """
    Remove the association of an ingredient from a recipe.

    :param recipe_id: The ID of the recipe.
    :param ingredient_id: The ID of the ingredient to remove.
    """
    from food_manager.models import RecipeIngredient
    recipe_ingredient = RecipeIngredient.query.filter_by(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id
    ).first_or_404()
    db.session.delete(recipe_ingredient)
    db.session.commit()


###############################################################################
# Recipe-Category Operations
###############################################################################

def add_category_to_recipe(recipe_id, category_id):
    """
    Associate a category with a recipe.

    :param recipe_id: The ID of the recipe.
    :param category_id: The ID of the category.
    :return: The created RecipeCategory association object.
    """
    from food_manager.models import RecipeCategory
    recipe_category = RecipeCategory(
        recipe_id=recipe_id,
        category_id=category_id
    )
    db.session.add(recipe_category)
    db.session.commit()
    return recipe_category


def remove_category_from_recipe(recipe_id, category_id):
    """
    Remove the association of a category from a recipe.

    :param recipe_id: The ID of the recipe.
    :param category_id: The ID of the category to remove.
    """
    from food_manager.models import RecipeCategory
    recipe_category = RecipeCategory.query.filter_by(
        recipe_id=recipe_id,
        category_id=category_id
    ).first_or_404()
    db.session.delete(recipe_category)
    db.session.commit()


###############################################################################
# Search and Filter Operations
###############################################################################

def search_recipes_by_ingredient(ingredient_name):
    """
    Search for recipes that include a given ingredient name.

    :param ingredient_name: The ingredient name to search for (case-insensitive).
    :return: A list of Recipe objects that match the search criteria.
    """
    from food_manager.models import Ingredient
    from food_manager.models import Recipe
    from food_manager.models import RecipeIngredient
    return Recipe.query.join(
        RecipeIngredient
    ).join(
        Ingredient
    ).filter(
        Ingredient.name.ilike(f'%{ingredient_name}%')
    ).all()


def search_recipes_by_category(category_name):
    """
    Search for recipes that belong to a given category name.

    :param category_name: The category name to search for (case-insensitive).
    :return: A list of Recipe objects that match the search criteria.
    """
    from food_manager.models import RecipeCategory
    from food_manager.models import Category
    from food_manager.models import Recipe
    return Recipe.query.join(
        RecipeCategory
    ).join(
        Category
    ).filter(
        Category.name.ilike(f'%{category_name}%')
    ).all()


def get_recipes_by_food(food_id):
    """
    Retrieve all recipes associated with a specific food item.

    :param food_id: The ID of the food item.
    :return: A list of Recipe objects associated with the given food ID.
    """
    from food_manager.models import Recipe
    return Recipe.query.filter_by(food_id=food_id).all()


def search_recipes_by_cooking_time(max_time):
    """
    Search for recipes that have a total cooking time (prep time + cook time) 
    within a specified limit.

    :param max_time: The maximum allowed total cooking time (in minutes).
    :return: A list of Recipe objects that match the search criteria.
    """
    from food_manager.models import Recipe
    return Recipe.query.filter(
        Recipe.cook_time + Recipe.prep_time <= max_time
    ).all()


def get_recipes_by_servings(servings):
    """
    Retrieve recipes that yield a specific number of servings.

    :param servings: The number of servings.
    :return: A list of Recipe objects that match the specified servings.
    """
    from food_manager.models import Recipe
    return Recipe.query.filter_by(servings=servings).all()


def get_low_calorie_recipes(max_calories):
    """
    Retrieve recipes that have nutritional information with calories under a specified threshold.

    :param max_calories: The maximum number of calories.
    :return: A list of Recipe objects that meet the low calorie criteria.
    """
    from food_manager.models import Recipe
    from food_manager.models import NutritionalInfo
    return Recipe.query.join(
        NutritionalInfo
    ).filter(
        NutritionalInfo.calories <= max_calories
    ).all()


###############################################################################
# Utility Operations
###############################################################################

def get_all_recipes_with_details():
    """
    Retrieve all recipes along with their related food, nutritional info,
    ingredients, and categories.

    :return: A list of Recipe objects with their details eagerly loaded.
    """
    from food_manager.models import Recipe
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).all()


def get_recipe_full_details(recipe_id):
    """
    Retrieve a single recipe with all related details (food, nutritional info,
    ingredients, and categories) eagerly loaded.

    :param recipe_id: The ID of the recipe.
    :return: The Recipe object with its full details or a 404 error if not found.
    """
    from food_manager.models import Recipe
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).get_or_404(recipe_id)
