from food_manager.models import (
    Food, Recipe, Ingredient, Category, NutritionalInfo,
    RecipeIngredient, RecipeCategory
)

class TestModelSerialization:
    def test_food_serialization(self, session):
        data = {'name': 'Rice', 'description': 'White', 'image_url': 'img.jpg'}
        obj = Food.deserialize(data)
        session.add(obj)
        session.commit()
        serialized = obj.serialize()
        assert serialized['name'] == data['name']
        assert 'food_id' in serialized

    def test_recipe_serialization(self, session):
        food = Food(name='Soup', description='Hot', image_url='img.jpg')
        session.add(food)
        session.commit()
        data = {
            'food_id': food.food_id,
            'instruction': 'Boil water',
            'prep_time': 5,
            'cook_time': 15,
            'servings': 2
        }
        recipe = Recipe.deserialize(data)
        session.add(recipe)
        session.commit()
        serialized = recipe.serialize()
        assert serialized['instruction'] == 'Boil water'
        assert serialized['food']['name'] == 'Soup'

    def test_ingredient_serialization(self, session):
        data = {'name': 'Salt', 'image_url': 'salt.jpg'}
        obj = Ingredient.deserialize(data)
        session.add(obj)
        session.commit()
        serialized = obj.serialize()
        assert serialized['name'] == 'Salt'
        assert 'ingredient_id' in serialized

    def test_category_serialization(self, session):
        data = {'name': 'Dinner', 'description': 'Evening meals'}
        obj = Category.deserialize(data)
        session.add(obj)
        session.commit()
        serialized = obj.serialize()
        assert serialized['name'] == 'Dinner'

    def test_nutritional_info_serialization(self, session):
        food = Food(name='Bar', description='Protein', image_url='img')
        recipe = Recipe(food=food, instruction='Unwrap and eat', prep_time=1, cook_time=0, servings=1)
        session.add_all([food, recipe])
        session.commit()
        data = {
            'recipe_id': recipe.recipe_id,
            'calories': 150,
            'protein': 10.0,
            'carbs': 15.0,
            'fat': 5.0
        }
        info = NutritionalInfo.deserialize(data)
        session.add(info)
        session.commit()
        serialized = info.serialize()
        assert serialized['calories'] == 150
        assert serialized['recipe_id'] == recipe.recipe_id

    def test_recipe_ingredient_serialization(self, session):
        food = Food(name='Cake', description='Sweet', image_url='cake.jpg')
        recipe = Recipe(food=food, instruction='Bake it', prep_time=15, cook_time=30, servings=4)
        ingredient = Ingredient(name='Flour', image_url='flour.jpg')
        session.add_all([food, recipe, ingredient])
        session.commit()
        data = {
            'recipe_id': recipe.recipe_id,
            'ingredient_id': ingredient.ingredient_id,
            'quantity': 200,
            'unit': 'grams'
        }
        ri = RecipeIngredient.deserialize(data)
        session.add(ri)
        session.commit()
        serialized = ri.serialize()
        assert serialized['unit'] == 'grams'

    def test_recipe_category_serialization(self, session):
        food = Food(name='Stew', description='Hearty', image_url='img')
        recipe = Recipe(food=food, instruction='Slow cook', prep_time=10, cook_time=60, servings=3)
        category = Category(name='Comfort', description='Warm meals')
        session.add_all([food, recipe, category])
        session.commit()
        data = {
            'recipe_id': recipe.recipe_id,
            'category_id': category.category_id
        }
        rc = RecipeCategory.deserialize(data)
        session.add(rc)
        session.commit()
        serialized = rc.serialize()
        assert serialized['recipe_id'] == recipe.recipe_id
