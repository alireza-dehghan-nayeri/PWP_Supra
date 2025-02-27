from models import *
from sqlalchemy import desc, text
from datetime import datetime

# Food Operations
def create_food(name, description=None, image_url=None):
    food = Food(name=name, description=description, image_url=image_url)
    db.session.add(food)
    db.session.commit()
    return food

def get_food(name):
    return Food.query.get_or_404(name)

def get_all_foods():
    return Food.query.all()

def update_food(name, new_name=None, description=None, image_url=None):
    food = Food.query.get_or_404(name)
    if new_name:
        food.name = new_name
    if description is not None:
        food.description = description
    if image_url is not None:
        food.image_url = image_url
    db.session.commit()
    return food

def delete_food(name):
    food = Food.query.get_or_404(name)
    db.session.delete(food)
    db.session.commit()

# Recipe Operations
def create_recipe(name, food_name, instruction, prep_time, cook_time, servings):
    recipe = Recipe(
        name=name,
        food_name=food_name,
        instruction=instruction,
        prep_time=prep_time,
        cook_time=cook_time,
        servings=servings
    )
    db.session.add(recipe)
    db.session.commit()
    return recipe

def get_recipe(name):
    return Recipe.query.get_or_404(name)

def get_all_recipes():
    return Recipe.query.all()

def update_recipe(name, new_name=None, food_name=None, instruction=None, prep_time=None, cook_time=None, servings=None):
    recipe = Recipe.query.get_or_404(name)
    if new_name:
        recipe.name = new_name
    if food_name is not None:
        recipe.food_name = food_name
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

def delete_recipe(name):
    recipe = Recipe.query.get_or_404(name)
    db.session.delete(recipe)
    db.session.commit()

# Ingredient Operations
def create_ingredient(name, image_url=None):
    ingredient = Ingredient(name=name, image_url=image_url)
    db.session.add(ingredient)
    db.session.commit()
    return ingredient

def get_ingredient(name):
    return Ingredient.query.get_or_404(name)

def get_all_ingredients():
    return Ingredient.query.all()

def update_ingredient(name, new_name=None, image_url=None):
    ingredient = Ingredient.query.get_or_404(name)
    if new_name:
        ingredient.name = new_name
    if image_url is not None:
        ingredient.image_url = image_url
    db.session.commit()
    return ingredient

def delete_ingredient(name):
    ingredient = Ingredient.query.get_or_404(name)
    db.session.delete(ingredient)
    db.session.commit()

# Category Operations
def create_category(name, description=None):
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return category

def get_category(name):
    return Category.query.get_or_404(name)

def get_all_categories():
    return Category.query.all()

def update_category(name, new_name=None, description=None):
    category = Category.query.get_or_404(name)
    if new_name:
        category.name = new_name
    if description is not None:
        category.description = description
    db.session.commit()
    return category

def delete_category(name):
    category = Category.query.get_or_404(name)
    db.session.delete(category)
    db.session.commit()

# Nutritional Info Operations
def create_nutritional_info(recipe_name, calories, protein, carbs, fat):
    nutritional_info = NutritionalInfo(
        recipe_name=recipe_name,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat
    )
    db.session.add(nutritional_info)
    db.session.commit()
    return nutritional_info

def get_nutritional_info(recipe_name):
    return NutritionalInfo.query.get_or_404(recipe_name)

def get_recipe_nutritional_info(recipe_name):
    return NutritionalInfo.query.filter_by(recipe_name=recipe_name).first_or_404()

def update_nutritional_info(recipe_name, calories=None, protein=None, carbs=None, fat=None):
    nutritional_info = NutritionalInfo.query.get_or_404(recipe_name)
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

def delete_nutritional_info(recipe_name):
    nutritional_info = NutritionalInfo.query.get_or_404(recipe_name)
    db.session.delete(nutritional_info)
    db.session.commit()

# Recipe-Ingredient Operations
def add_ingredient_to_recipe(recipe_name, ingredient_name, quantity, unit='piece'):
    recipe = Recipe.query.get_or_404(recipe_name)
    ingredient = Ingredient.query.get_or_404(ingredient_name)

    # Check if the ingredient is already linked to the recipe
    existing_link = db.session.execute(text("""
        SELECT 1 FROM recipe_ingredient WHERE recipe_name=:recipe_name AND ingredient_name=:ingredient_name
    """), {'recipe_name': recipe_name, 'ingredient_name': ingredient_name}).fetchone()

    if existing_link:
        # If exists, update instead of inserting
        stmt = text("""
            UPDATE recipe_ingredient
            SET quantity = :quantity, unit = :unit
            WHERE recipe_name = :recipe_name AND ingredient_name = :ingredient_name
        """)
    else:
        # Insert only if it does not exist
        stmt = text("""
            INSERT INTO recipe_ingredient (recipe_name, ingredient_name, quantity, unit)
            VALUES (:recipe_name, :ingredient_name, :quantity, :unit)
        """)

    db.session.execute(stmt, {
        'recipe_name': recipe_name,
        'ingredient_name': ingredient_name,
        'quantity': quantity,
        'unit': unit
    })

    db.session.commit()
    return recipe

def update_recipe_ingredient(recipe_name, ingredient_name, quantity=None, unit=None):
    Recipe.query.get_or_404(recipe_name)
    Ingredient.query.get_or_404(ingredient_name)
    
    stmt = text("""
        UPDATE recipe_ingredient
        SET quantity = COALESCE(:quantity, quantity),
            unit = COALESCE(:unit, unit)
        WHERE recipe_name = :recipe_name AND ingredient_name = :ingredient_name
    """)
    
    result = db.session.execute(stmt, {
        'recipe_name': recipe_name,
        'ingredient_name': ingredient_name,
        'quantity': quantity,
        'unit': unit
    })
    
    if result.rowcount == 0:
        from werkzeug.exceptions import NotFound
        raise NotFound(f"No relationship between recipe '{recipe_name}' and ingredient '{ingredient_name}'")
    
    db.session.commit()
    return get_recipe(recipe_name)

def remove_ingredient_from_recipe(recipe_name, ingredient_name):
    recipe = Recipe.query.get_or_404(recipe_name)
    ingredient = Ingredient.query.get_or_404(ingredient_name)
    
    if ingredient in recipe.ingredients:
        recipe.ingredients.remove(ingredient)
    
    db.session.commit()

# Recipe-Category Operations
def add_category_to_recipe(recipe_name, category_name):
    recipe = Recipe.query.get_or_404(recipe_name)
    category = Category.query.get_or_404(category_name)
    
    if category not in recipe.categories:
        recipe.categories.append(category)
        db.session.commit()
    
    return recipe

def remove_category_from_recipe(recipe_name, category_name):
    recipe = Recipe.query.get_or_404(recipe_name)
    category = Category.query.get_or_404(category_name)
    
    if category in recipe.categories:
        recipe.categories.remove(category)
        db.session.commit()

# Search and Filter Operations
def search_recipes_by_ingredient(ingredient_name):
    return Recipe.query.filter(
        Recipe.ingredients.any(Ingredient.name.ilike(f'%{ingredient_name}%'))
    ).all()

def search_recipes_by_category(category_name):
    return Recipe.query.filter(
        Recipe.categories.any(Category.name.ilike(f'%{category_name}%'))
    ).all()

def get_recipes_by_food(food_name):
    return Recipe.query.filter_by(food_name=food_name).all()

def search_recipes_by_cooking_time(max_time):
    return Recipe.query.filter(
        Recipe.cook_time + Recipe.prep_time <= max_time
    ).all()

def get_recipes_by_servings(servings):
    return Recipe.query.filter_by(servings=servings).all()

def get_low_calorie_recipes(max_calories):
    return Recipe.query.join(
        NutritionalInfo, Recipe.name == NutritionalInfo.recipe_name
    ).filter(
        NutritionalInfo.calories <= max_calories
    ).all()
