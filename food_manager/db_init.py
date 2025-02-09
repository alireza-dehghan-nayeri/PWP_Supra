from flask.cli import with_appcontext
from db_operations import *
from models import *
import click

def init_app(app):
    """Initialize the database with the app"""
    app.cli.add_command(init_db_command)
    app.cli.add_command(sample_data_command)
    app.cli.add_command(clear_db_command)
    # app.cli.add_command(test_ondelete)
    # app.cli.add_command(test_constraints)

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db.drop_all() 
    db.create_all()
    click.echo('Initialized the database.')

@click.command('clear-db')
@with_appcontext
def clear_db_command():
    """Clear all data from the database while preserving tables."""
    try:
        RecipeCategory.query.delete()
        RecipeIngredient.query.delete()
        
        NutritionalInfo.query.delete()
        Recipe.query.delete()
        Food.query.delete()
        Ingredient.query.delete()
        Category.query.delete()
        
        db.session.commit()
        click.echo('Cleared all data from the database.')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error clearing database: {str(e)}')

@click.command('sample-data')
@with_appcontext
def sample_data_command():
    """Add sample data to the database."""
    try:
        # Add sample foods
        foods_data = [
            {'name': 'Pizza', 'description': 'Italian flatbread topped with various ingredients'},
            {'name': 'Pasta', 'description': 'Italian noodles with sauce'},
            {'name': 'Salad', 'description': 'Fresh mixed vegetables with dressing'},
            {'name': 'Soup', 'description': 'Warm liquid food with various ingredients'}
        ]
        foods = {food['name']: create_food(**food) for food in foods_data}
        
        # Add sample ingredients
        ingredients_data = [
            {'name': 'Flour', 'image_url': 'flour.jpg'},
            {'name': 'Tomato', 'image_url': 'tomato.jpg'},
            {'name': 'Cheese', 'image_url': 'cheese.jpg'},
            {'name': 'Basil', 'image_url': 'basil.jpg'},
            {'name': 'Olive Oil', 'image_url': 'olive_oil.jpg'},
            {'name': 'Garlic', 'image_url': 'garlic.jpg'},
            {'name': 'Salt', 'image_url': 'salt.jpg'},
            {'name': 'Pepper', 'image_url': 'pepper.jpg'}
        ]
        ingredients = {ing['name']: create_ingredient(**ing) for ing in ingredients_data}
        
        # Add sample categories
        categories_data = [
            {'name': 'Italian', 'description': 'Traditional Italian cuisine'},
            {'name': 'Vegetarian', 'description': 'Meat-free dishes'},
            {'name': 'Quick & Easy', 'description': 'Ready in 30 minutes or less'},
            {'name': 'Healthy', 'description': 'Nutritious and balanced meals'}
        ]
        categories = {cat['name']: create_category(**cat) for cat in categories_data}
        
        # Add sample recipes
        recipes_data = [
            {
                'name': 'Margherita Pizza',
                'food': foods['Pizza'],
                'instruction': ('1. Make dough with flour, water, and yeast\n'
                              '2. Spread tomato sauce\n'
                              '3. Add fresh mozzarella and basil\n'
                              '4. Bake at 450°F for 15 minutes'),
                'prep_time': 30,
                'cook_time': 15,
                'servings': 4,
                'ingredients': [
                    {'ingredient': ingredients['Flour'], 'quantity': 500, 'unit': 'g'},
                    {'ingredient': ingredients['Tomato'], 'quantity': 200, 'unit': 'g'},
                    {'ingredient': ingredients['Cheese'], 'quantity': 150, 'unit': 'g'},
                    {'ingredient': ingredients['Basil'], 'quantity': 10, 'unit': 'leaves'},
                    {'ingredient': ingredients['Olive Oil'], 'quantity': 2, 'unit': 'tbsp'}
                ],
                'categories': [categories['Italian'], categories['Vegetarian']],
                'nutrition': {
                    'calories': 266,
                    'protein': 11,
                    'carbs': 33,
                    'fat': 9
                }
            },
            {
                'name': 'Garlic Pasta',
                'food': foods['Pasta'],
                'instruction': ('1. Cook pasta in salted water\n'
                              '2. Sauté garlic in olive oil\n'
                              '3. Toss pasta with garlic oil\n'
                              '4. Add cheese and pepper'),
                'prep_time': 10,
                'cook_time': 15,
                'servings': 2,
                'ingredients': [
                    {'ingredient': ingredients['Garlic'], 'quantity': 4, 'unit': 'cloves'},
                    {'ingredient': ingredients['Olive Oil'], 'quantity': 3, 'unit': 'tbsp'},
                    {'ingredient': ingredients['Cheese'], 'quantity': 50, 'unit': 'g'},
                    {'ingredient': ingredients['Salt'], 'quantity': 1, 'unit': 'tsp'},
                    {'ingredient': ingredients['Pepper'], 'quantity': 0.5, 'unit': 'tsp'}
                ],
                'categories': [categories['Italian'], categories['Quick & Easy']],
                'nutrition': {
                    'calories': 320,
                    'protein': 9,
                    'carbs': 42,
                    'fat': 14
                }
            }
        ]
        
        # Create recipes with all related data
        for recipe_data in recipes_data:
            # Create base recipe
            recipe = create_recipe(
                food_id=recipe_data['food'].food_id,
                instruction=recipe_data['instruction'],
                prep_time=recipe_data['prep_time'],
                cook_time=recipe_data['cook_time'],
                servings=recipe_data['servings']
            )
            
            # Add ingredients
            for ing_data in recipe_data['ingredients']:
                add_ingredient_to_recipe(
                    recipe_id=recipe.recipe_id,
                    ingredient_id=ing_data['ingredient'].ingredient_id,
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit']
                )
            
            # Add categories
            for category in recipe_data['categories']:
                add_category_to_recipe(
                    recipe_id=recipe.recipe_id,
                    category_id=category.category_id
                )
            
            # Add nutritional info
            create_nutritional_info(
                recipe_id=recipe.recipe_id,
                **recipe_data['nutrition']
            )
        
        click.echo('Added sample data to the database.')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error adding sample data: {str(e)}')
        raise e