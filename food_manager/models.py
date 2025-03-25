"""Models for Food Manager.

This module defines the SQLAlchemy models for the application.
"""

from sqlalchemy import CheckConstraint
from food_manager import db


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
