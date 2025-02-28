from food_manager import db

# Food Operations
def create_food(name, description=None, image_url=None):
    from food_manager.models import Food
    existing_food = Food.query.filter_by(name=name).first()
    if existing_food:
        raise ValueError(f"Food with name '{name}' already exists.")

    food = Food(name=name, description=description, image_url=image_url)
    db.session.add(food)
    db.session.commit()
    return food


def get_food_by_id(food_id):
    from food_manager.models import Food
    return Food.query.get_or_404(food_id)

def get_all_foods():
    from food_manager.models import Food
    return Food.query.all()

def update_food(food_id, name=None, description=None, image_url=None):
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
    from food_manager.models import Food
    food = Food.query.get_or_404(food_id)
    db.session.delete(food)
    db.session.commit()

# Recipe Operations
def create_recipe(food_id, instruction, prep_time, cook_time, servings):
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
    from food_manager.models import Recipe
    return Recipe.query.get_or_404(recipe_id)

def get_all_recipes():
    from food_manager.models import Recipe
    return Recipe.query.all()

def update_recipe(recipe_id, food_id=None, instruction=None, prep_time=None, cook_time=None, servings=None):
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
    from food_manager.models import Recipe
    recipe = Recipe.query.get_or_404(recipe_id)
    db.session.delete(recipe)
    db.session.commit()

# Ingredient Operations
def create_ingredient(name, image_url=None):
    from food_manager.models import Ingredient
    ingredient = Ingredient(name=name, image_url=image_url)
    db.session.add(ingredient)
    db.session.commit()
    return ingredient

def get_ingredient_by_id(ingredient_id):
    from food_manager.models import Ingredient
    return Ingredient.query.get_or_404(ingredient_id)

def get_all_ingredients():
    from food_manager.models import Ingredient
    return Ingredient.query.all()

def update_ingredient(ingredient_id, name=None, image_url=None):
    from food_manager.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    if name:
        ingredient.name = name
    if image_url is not None:
        ingredient.image_url = image_url
    db.session.commit()
    return ingredient

def delete_ingredient(ingredient_id):
    from food_manager.models import Ingredient
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()

# Category Operations
def create_category(name, description=None):
    from food_manager.models import Category
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return category

def get_category_by_id(category_id):
    from food_manager.models import Category
    return Category.query.get_or_404(category_id)

def get_all_categories():
    from food_manager.models import Category
    return Category.query.all()

def update_category(category_id, name=None, description=None):
    from food_manager.models import Category
    category = Category.query.get_or_404(category_id)
    if name:
        category.name = name
    if description is not None:
        category.description = description
    db.session.commit()
    return category

def delete_category(category_id):
    from food_manager.models import Category
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

# Nutritional Info Operations
def create_nutritional_info(recipe_id, calories, protein, carbs, fat):
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
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.all()

def get_nutritional_info_by_id(nutritional_info_id):
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.get_or_404(nutritional_info_id)

def get_recipe_nutritional_info(recipe_id):
    from food_manager.models import NutritionalInfo
    return NutritionalInfo.query.filter_by(recipe_id=recipe_id).first_or_404()

def update_nutritional_info(nutritional_info_id, calories=None, protein=None, carbs=None, fat=None):
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
    from food_manager.models import NutritionalInfo
    nutritional_info = NutritionalInfo.query.get_or_404(nutritional_info_id)
    db.session.delete(nutritional_info)
    db.session.commit()

# Recipe-Ingredient Operations
def add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit='piece'):
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
    from food_manager.models import RecipeIngredient
    recipe_ingredient = RecipeIngredient.query.filter_by(
        recipe_id=recipe_id,
        ingredient_id=ingredient_id
    ).first_or_404()
    db.session.delete(recipe_ingredient)
    db.session.commit()

# Recipe-Category Operations
def add_category_to_recipe(recipe_id, category_id):
    from food_manager.models import RecipeCategory
    recipe_category = RecipeCategory(
        recipe_id=recipe_id,
        category_id=category_id
    )
    db.session.add(recipe_category)
    db.session.commit()
    return recipe_category

def remove_category_from_recipe(recipe_id, category_id):
    from food_manager.models import RecipeCategory
    recipe_category = RecipeCategory.query.filter_by(
        recipe_id=recipe_id,
        category_id=category_id
    ).first_or_404()
    db.session.delete(recipe_category)
    db.session.commit()
# Search and Filter Operations
def search_recipes_by_ingredient(ingredient_name):
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
    from food_manager.models import Recipe
    return Recipe.query.filter_by(food_id=food_id).all()

def search_recipes_by_cooking_time(max_time):
    from food_manager.models import Recipe
    return Recipe.query.filter(
        Recipe.cook_time + Recipe.prep_time <= max_time
    ).all()

def get_recipes_by_servings(servings):
    from food_manager.models import Recipe
    return Recipe.query.filter_by(servings=servings).all()

def get_low_calorie_recipes(max_calories):
    from food_manager.models import Recipe
    from food_manager.models import NutritionalInfo
    return Recipe.query.join(
        NutritionalInfo
    ).filter(
        NutritionalInfo.calories <= max_calories
    ).all()

# Utility Operations
def get_all_recipes_with_details():
    from food_manager.models import Recipe
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).all()

def get_recipe_full_details(recipe_id):
    from food_manager.models import Recipe
    return Recipe.query.options(
        db.joinedload(Recipe.food),
        db.joinedload(Recipe.nutritional_info),
        db.joinedload(Recipe.ingredients),
        db.joinedload(Recipe.categories)
    ).get_or_404(recipe_id)