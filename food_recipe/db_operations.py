from models import *

from sqlalchemy import desc
from datetime import datetime

# Food Operations
def create_food(name, description=None, image_url=None):
    food = Food(name=name, description=description, image_url=image_url)
    db.session.add(food)
    db.session.commit()
    return food

def get_food(food_id):
    return Food.query.get_or_404(food_id)

def get_all_foods():
    return Food.query.all()

def update_food(food_id, name=None, description=None, image_url=None):
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
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()

# Recipe Operations
def create_recipe(food_id, instruction, prep_time, cook_time, servings):
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

def get_recipe(recipe_id):
    return Recipe.query.get_or_404(recipe_id)

def get_all_recipes():
    return Recipe.query.all()

def update_recipe(recipe_id, food_id=None, instruction=None, prep_time=None, cook_time=None, servings=None):
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
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()

# Ingredient Operations
def create_ingredient(name, image_url=None):
    ingredient = Ingredient(name=name, image_url=image_url)
    db.session.add(ingredient)
    db.session.commit()
    return ingredient

def get_ingredient(ingredient_id):
    return Ingredient.query.get_or_404(ingredient_id)

def get_all_ingredients():
    return Ingredient.query.all()

def update_ingredient(ingredient_id, name=None, image_url=None):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    if name:
        ingredient.name = name
    if image_url is not None:
        ingredient.image_url = image_url
    db.session.commit()
    return ingredient

def delete_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()

# Category Operations
def create_category(name, description=None):
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return category

def get_category(category_id):
    return Category.query.get_or_404(category_id)

def get_all_categories():
    return Category.query.all()

def update_category(category_id, name=None, description=None):
    category = Category.query.get_or_404(category_id)
    if name:
        category.name = name
    if description is not None:
        category.description = description
    db.session.commit()
    return category

def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

# Nutritional Info Operations
def create_nutritional_info(recipe_id, calories, protein, carbs, fat):
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

def get_nutritional_info(nutritional_info_id):
    return NutritionalInfo.query.get_or_404(nutritional_info_id)

def get_recipe_nutritional_info(recipe_id):
    return NutritionalInfo.query.filter_by(recipe_id=recipe_id).first_or_404()

def update_nutritional_info(nutritional_info_id, calories=None, protein=None, carbs=None, fat=None):
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
    nutritional_info = NutritionalInfo.query.get_or_404(nutritional_info_id)
    db.session.delete(nutritional_info)
    db.session.commit()

# Recipe-Ingredient Operations
def add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit='piece'):
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
    recipe_ingredient = RecipeIngredient.query.filter_by(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id
    ).first_or_404()
    db.session.delete(recipe_ingredient)
    db.session.commit()

# Recipe-Category Operations
def add_category_to_recipe(recipe_id, category_id):
    recipe_category = RecipeCategory(
        recipe_id=recipe_id,
        category_id=category_id
    )
    db.session.add(recipe_category)
    db.session.commit()
    return recipe_category

def remove_category_from_recipe(recipe_id, category_id):
    recipe_category = RecipeCategory.query.filter_by(
        recipe_id=recipe_id,
        category_id=category_id
    ).first_or_404()
    db.session.delete(recipe_category)
    db.session.commit()

# Search and Filter Operations
def search_recipes_by_ingredient(ingredient_name):
    return Recipe.query.join(
        RecipeIngredient
    ).join(
        Ingredient
    ).filter(
        Ingredient.name.ilike(f'%{ingredient_name}%')
    ).all()

def search_recipes_by_category(category_name):
    return Recipe.query.join(
        RecipeCategory
    ).join(
        Category
    ).filter(
        Category.name.ilike(f'%{category_name}%')
    ).all()

def get_recipes_by_food(food_id):
    return Recipe.query.filter_by(food_id=food_id).all()

def search_recipes_by_cooking_time(max_time):
    return Recipe.query.filter(
        Recipe.cook_time + Recipe.prep_time <= max_time
    ).all()

def get_recipes_by_servings(servings):
    return Recipe.query.filter_by(servings=servings).all()

def get_low_calorie_recipes(max_calories):
    return Recipe.query.join(
        NutritionalInfo
    ).filter(
        NutritionalInfo.calories <= max_calories
    ).all()

# Utility Operations
def get_all_recipes_with_details():
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).all()

def get_recipe_full_details(recipe_id):
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).get_or_404(recipe_id)