"""Models and CLI Commands for Food Manager.

This module defines the SQLAlchemy models for the application along with CLI
commands to initialize, clear, and populate the database with sample data.
"""

import click
from sqlalchemy import CheckConstraint
from flask.cli import with_appcontext

from food_manager import db
from food_manager.db_operations import add_category_to_recipe, add_ingredient_to_recipe, create_category, create_food, create_ingredient, create_nutritional_info, create_recipe
#

###############################################################################
# Model Definitions
###############################################################################

class Food(db.Model):
    """Food model representing food items."""
    __tablename__ = 'food'
    food_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    # Relationships
    recipes = db.relationship(
        'Recipe',
        back_populates='food',
        cascade="all, delete-orphan",
        lazy='dynamic'
    )

    def __repr__(self):
        """Return the string representation of the Food object."""
        return f'<Food {self.name}>'

    def serialize(self):
        """
        Serialize the Food object to a dictionary.

        :return: Dictionary containing food_id, name, description, and image_url.
        """
        return {
            'food_id': self.food_id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url
        }

    @staticmethod
    def deserialize(data):
        """
        Create a Food instance from a dictionary.

        :param data: Dictionary with keys 'name', 'description', and 'image_url'.
        :return: Food object.
        """
        return Food(
            name=data.get('name'),
            description=data.get('description'),
            image_url=data.get('image_url')
        )


class Recipe(db.Model):
    """Recipe model representing recipes associated with food items."""
    __tablename__ = 'recipe'

    recipe_id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(
        db.Integer,
        db.ForeignKey('food.food_id', ondelete="CASCADE"),
        nullable=False
    )
    instruction = db.Column(db.String(255), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    servings = db.Column(db.Integer, nullable=False)

    # Relationships
    food = db.relationship('Food', back_populates='recipes')
    nutritional_info = db.relationship(
        'NutritionalInfo',
        back_populates='recipe',
        cascade="all, delete-orphan",
        uselist=False
    )
    ingredients = db.relationship(
        'Ingredient',
        secondary='recipe_ingredient',
        cascade="all, delete",
        back_populates='recipes'
    )
    categories = db.relationship(
        'Category',
        secondary='recipe_category',
        cascade="all, delete",
        back_populates='recipes'
    )

    __table_args__ = (
        CheckConstraint("prep_time >= 0", name="prep_time_constraint"),
        CheckConstraint("cook_time >= 0", name="cook_time_constraint"),
        CheckConstraint("servings > 0", name="servings_constraint"),
    )

    def __repr__(self):
        """
        Return the string representation of the Recipe object.

        :return: String with recipe_id and associated food name.
        """
        return f'<Recipe {self.recipe_id} for {self.food.name}>'

    def serialize(self):
        """
        Serialize the Recipe object to a dictionary including related objects.

        :return: Dictionary with recipe details and nested serialized food,
                 nutritional_info, ingredients, and categories.
        """
        return {
            'recipe_id': self.recipe_id,
            'food_id': self.food_id,
            'instruction': self.instruction,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'food': self.food.serialize(),
            'nutritional_info': (
                self.nutritional_info.serialize() if self.nutritional_info else None
            ),
            'ingredients': [
                {
                    'ingredient': ing.serialize(),
                    'quantity': next(
                        (
                            ri.quantity for ri in RecipeIngredient.query.filter_by(
                                recipe_id=self.recipe_id,
                                ingredient_id=ing.ingredient_id
                            )
                        ),
                        None
                    ),
                    'unit': next(
                        (
                            ri.unit for ri in RecipeIngredient.query.filter_by(
                                recipe_id=self.recipe_id,
                                ingredient_id=ing.ingredient_id
                            )
                        ),
                        None
                    )
                }
                for ing in self.ingredients
            ],
            'categories': [cat.serialize() for cat in self.categories]
        }

    @staticmethod
    def deserialize(data):
        """
        Create a Recipe instance from a dictionary.

        :param data: Dictionary with keys 'food_id', 'instruction', 'prep_time',
                     'cook_time', and 'servings'.
        :return: Recipe object.
        """
        return Recipe(
            food_id=data.get('food_id'),
            instruction=data.get('instruction'),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings'),
        )


class Ingredient(db.Model):
    """Ingredient model representing ingredients used in recipes."""
    __tablename__ = 'ingredient'

    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    # Relationships
    recipes = db.relationship(
        'Recipe',
        secondary='recipe_ingredient',
        cascade="all, delete",
        back_populates='ingredients'
    )

    def __repr__(self):
        """Return the string representation of the Ingredient object."""
        return f'<Ingredient {self.name}>'

    def serialize(self):
        """
        Serialize the Ingredient object to a dictionary.

        :return: Dictionary containing ingredient_id, name, and image_url.
        """
        return {
            'ingredient_id': self.ingredient_id,
            'name': self.name,
            'image_url': self.image_url
        }

    @staticmethod
    def deserialize(data):
        """
        Create an Ingredient instance from a dictionary.

        :param data: Dictionary with keys 'name' and 'image_url'.
        :return: Ingredient object.
        """
        return Ingredient(
            name=data.get('name'),
            image_url=data.get('image_url')
        )


class Category(db.Model):
    """Category model representing recipe categories."""
    __tablename__ = 'category'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    recipes = db.relationship(
        'Recipe',
        secondary='recipe_category',
        cascade="all, delete",
        back_populates='categories'
    )

    def __repr__(self):
        """Return the string representation of the Category object."""
        return f'<Category {self.name}>'

    def serialize(self):
        """
        Serialize the Category object to a dictionary.

        :return: Dictionary containing category_id, name, and description.
        """
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description
        }

    @staticmethod
    def deserialize(data):
        """
        Create a Category instance from a dictionary.

        :param data: Dictionary with keys 'name' and 'description'.
        :return: Category object.
        """
        return Category(
            name=data.get('name'),
            description=data.get('description')
        )


class NutritionalInfo(db.Model):
    """NutritionalInfo model representing nutritional details for a recipe."""
    __tablename__ = 'nutritional_info'

    nutritional_info_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id', ondelete="CASCADE"),
        unique=True,
        nullable=False
    )
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)

    # Relationships
    recipe = db.relationship('Recipe', back_populates='nutritional_info')

    __table_args__ = (
        CheckConstraint("calories >= 0", name="calories_constraint"),
        CheckConstraint("protein >= 0", name="protein_constraint"),
        CheckConstraint("carbs >= 0", name="carbs_constraint"),
        CheckConstraint("fat >= 0", name="fat_constraint"),
    )

    def __repr__(self):
        """Return the string representation of the NutritionalInfo object."""
        return f'<NutritionalInfo for recipe {self.recipe_id}>'

    def serialize(self):
        """
        Serialize the NutritionalInfo object to a dictionary.

        :return: Dictionary containing nutritional_info_id, recipe_id, calories, protein, carbs, and fat.
        """
        return {
            'nutritional_info_id': self.nutritional_info_id,
            'recipe_id': self.recipe_id,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat
        }

    @staticmethod
    def deserialize(data):
        """
        Create a NutritionalInfo instance from a dictionary.

        :param data: Dictionary with keys 'recipe_id', 'calories', 'protein', 'carbs', and 'fat'.
        :return: NutritionalInfo object.
        """
        return NutritionalInfo(
            recipe_id=data.get('recipe_id'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            carbs=data.get('carbs'),
            fat=data.get('fat')
        )


class RecipeIngredient(db.Model):
    """Association model representing the relationship between recipes and ingredients."""
    __tablename__ = 'recipe_ingredient'

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id', ondelete="CASCADE"),
        primary_key=True
    )
    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey('ingredient.ingredient_id', ondelete="CASCADE"),
        primary_key=True
    )
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(64), nullable=False, default='piece')

    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_constraint"),
    )

    def __repr__(self):
        """Return the string representation of the RecipeIngredient object."""
        return f'<RecipeIngredient {self.recipe_id}:{self.ingredient_id}>'

    def serialize(self):
        """
        Serialize the RecipeIngredient object to a dictionary.

        :return: Dictionary containing recipe_id, ingredient_id, quantity, and unit.
        """
        return {
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'quantity': self.quantity,
            'unit': self.unit
        }

    @staticmethod
    def deserialize(data):
        """
        Create a RecipeIngredient instance from a dictionary.

        :param data: Dictionary with keys 'recipe_id', 'ingredient_id', 'quantity', and 'unit'.
        :return: RecipeIngredient object.
        """
        return RecipeIngredient(
            recipe_id=data.get('recipe_id'),
            ingredient_id=data.get('ingredient_id'),
            quantity=data.get('quantity'),
            unit=data.get('unit')
        )


class RecipeCategory(db.Model):
    """Association model representing the relationship between recipes and categories."""
    __tablename__ = 'recipe_category'

    recipe_id = db.Column(
        db.Integer,
        db.ForeignKey('recipe.recipe_id', ondelete="CASCADE"),
        primary_key=True
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.category_id', ondelete="CASCADE"),
        primary_key=True
    )

    def __repr__(self):
        """Return the string representation of the RecipeCategory object."""
        return f'<RecipeCategory {self.recipe_id}:{self.category_id}>'

    def serialize(self):
        """
        Serialize the RecipeCategory object to a dictionary.

        :return: Dictionary containing recipe_id and category_id.
        """
        return {
            'recipe_id': self.recipe_id,
            'category_id': self.category_id
        }

    @staticmethod
    def deserialize(data):
        """
        Create a RecipeCategory instance from a dictionary.

        :param data: Dictionary with keys 'recipe_id' and 'category_id'.
        :return: RecipeCategory object.
        """
        return RecipeCategory(
            recipe_id=data.get('recipe_id'),
            category_id=data.get('category_id')
        )

###############################################################################
# CLI Command Definitions
###############################################################################

def init_app(app):
    """
    Initialize the Flask application with custom CLI commands.

    :param app: The Flask application instance.
    """
    app.cli.add_command(init_db_command)
    app.cli.add_command(sample_data_command)
    app.cli.add_command(clear_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    CLI command to drop all tables and create new ones.

    This command clears existing data and creates fresh database tables.
    """
    db.drop_all()
    db.create_all()
    click.echo('Initialized the database.')


@click.command('clear-db')
@with_appcontext
def clear_db_command():
    """
    CLI command to clear all data from the database while preserving tables.

    This command deletes all records from association and main tables.
    """
    try:
        # Delete records from association tables first
        RecipeCategory.query.delete()
        RecipeIngredient.query.delete()

        # Delete records from main tables
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
    """
    CLI command to add sample data to the database.

    This command populates the database with sample foods, ingredients, categories,
    recipes, and nutritional information.
    """
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
                'instruction': (
                    '1. Make dough with flour, water, and yeast\n'
                    '2. Spread tomato sauce\n'
                    '3. Add fresh mozzarella and basil\n'
                    '4. Bake at 450°F for 15 minutes'
                ),
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
                'instruction': (
                    '1. Cook pasta in salted water\n'
                    '2. Sauté garlic in olive oil\n'
                    '3. Toss pasta with garlic oil\n'
                    '4. Add cheese and pepper'
                ),
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

            # Add ingredients to the recipe
            for ing_data in recipe_data['ingredients']:
                add_ingredient_to_recipe(
                    recipe_id=recipe.recipe_id,
                    ingredient_id=ing_data['ingredient'].ingredient_id,
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit']
                )

            # Add categories to the recipe
            for category in recipe_data['categories']:
                add_category_to_recipe(
                    recipe_id=recipe.recipe_id,
                    category_id=category.category_id
                )

            # Add nutritional info to the recipe
            create_nutritional_info(
                recipe_id=recipe.recipe_id,
                **recipe_data['nutrition']
            )

        click.echo('Added sample data to the database.')

    except Exception as e:
        db.session.rollback()
        click.echo(f'Error adding sample data: {str(e)}')
        raise e