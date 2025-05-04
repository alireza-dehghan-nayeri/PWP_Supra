"""Models for Food Manager.

This module defines the SQLAlchemy models for the application.
"""
from flask import url_for
from sqlalchemy import CheckConstraint
from food_manager import db
from food_manager.constants import FOOD_PROFILE, NAMESPACE, LINK_RELATIONS_URL, RECIPE_PROFILE, INGREDIENT_PROFILE, \
    CATEGORY_PROFILE, NUTRITION_PROFILE


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

    @staticmethod
    def get_schema() -> dict:
        """
        Schema for the Food model.

        :return: Food schema
        """
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "image_url": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        }

    def serialize(self, short_form=False):
        """
        Serialize the Food object to a dictionary.

        :return: Dictionary containing food_id, name, description, and image_url.
        """

        from food_manager.builder import FoodManagerBuilder

        data = FoodManagerBuilder(
            food_id=self.food_id,
            name=self.name,
            description=self.description,
            image_url=self.image_url,
        )

        if short_form:
            data.add_control("self", href=url_for("api.foodresource", food_id=self))
            data.add_control("profile", href=FOOD_PROFILE)
            return data

        data.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        data.add_control("self", href=url_for("api.foodresource", food_id=self))
        data.add_control("profile", href=FOOD_PROFILE)
        data.add_control("collection", href=url_for("api.foodlistresource"))

        if self.recipes.count() == 0:
            data.add_control_add_recipe(food_id=self.food_id)

        data.add_control_edit_food(self)
        data.add_control_delete_food(self)
        data["recipes"] = [recipe.serialize(short_form=True) for recipe in self.recipes]

        return data

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

    @staticmethod
    def get_schema(default_food_id=None) -> dict:
        """Schema for the Recipe model.

        :param default_food_id: Optional default value for food_id
        :return: recipe schema
        """
        schema = {
            "type": "object",
            "properties": {
                "food_id": {
                    "type": "number",
                    **({"default": default_food_id} if default_food_id is not None else {})
                },
                "instruction": {"type": "string"},
                "prep_time": {"type": "number", "minimum": 0},
                "cook_time": {"type": "number", "minimum": 0},
                "servings": {"type": "number", "minimum": 1},
            },
            "required": ["food_id", "instruction", "prep_time", "cook_time", "servings"],
            "additionalProperties": False,
        }
        return schema

    def serialize(self, short_form=False):
        """
        Serialize the Recipe object to a dictionary including related objects.

        :return: Dictionary with recipe details and nested serialized food,
                 nutritional_info, ingredients, and categories.
        """

        from food_manager.builder import FoodManagerBuilder

        data = FoodManagerBuilder(
            recipe_id=self.recipe_id,
            food_id=self.food_id,
            instruction=self.instruction,
            prep_time=self.prep_time,
            cook_time=self.cook_time,
            servings=self.servings,
            food=self.food.name
        )

        if short_form:
            data.add_control("self", href=url_for("api.reciperesource", recipe_id=self))
            data.add_control("profile", href=RECIPE_PROFILE)
            return data

        data.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        data.add_control("self", href=url_for("api.reciperesource", recipe_id=self))
        data.add_control("profile", href=RECIPE_PROFILE)
        data.add_control("collection", href=url_for("api.recipelistresource"))
        data.add_control_food(self)
        data.add_control_edit_recipe(recipe=self, food_id=self.food_id)
        data.add_control_delete_recipe(self)

        data["nutritional_info"] = self.nutritional_info.serialize() if self.nutritional_info else None
        data["categories"] = [cat.serialize() for cat in self.categories]
        data["ingredients"] = [
            {
                "ingredient": ing.serialize(),
                "quantity": next(
                    (
                        ri.quantity for ri in RecipeIngredient.query.filter_by(
                        recipe_id=self.recipe_id,
                        ingredient_id=ing.ingredient_id
                    )
                    ),
                    None
                ),
                "unit": next(
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
        ]

        return data

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

    @staticmethod
    def get_schema() -> dict:
        """Schema for the Ingredient model.

        :return: ingredient schema
        """
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "image_url": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        }

    def serialize(self):
        """
        Serialize the Ingredient object to a dictionary.

        :return: Dictionary containing ingredient_id, name, and image_url.
        """

        from food_manager.builder import FoodManagerBuilder

        data = FoodManagerBuilder(
            ingredient_id=self.ingredient_id,
            name=self.name,
            image_url=self.image_url,
        )
        data.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        data.add_control("self", href=url_for("api.ingredientresource", ingredient_id=self))
        data.add_control("profile", href=INGREDIENT_PROFILE)
        data.add_control("collection", href=url_for("api.ingredientlistresource"))
        data.add_control_edit_ingredient(self)
        data.add_control_delete_ingredient(self)

        return data

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

    @staticmethod
    def get_schema() -> dict:
        """Schema for the Category model.

        :return: Category schema
        """
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        }

    def serialize(self):
        """
        Serialize the Category object to a dictionary.

        :return: Dictionary containing category_id, name, and description.
        """

        from food_manager.builder import FoodManagerBuilder

        data = FoodManagerBuilder(
            category_id=self.category_id,
            name=self.name,
            description=self.description,
        )
        data.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        data.add_control("self", href=url_for("api.categoryresource", category_id=self))
        data.add_control("profile", href=CATEGORY_PROFILE)
        data.add_control("collection", href=url_for("api.categorylistresource"))
        data.add_control_edit_category(self)
        data.add_control_delete_category(self)

        return data

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

    @staticmethod
    def get_schema(default_recipe_id=None) -> dict:
        """Schema for the NutritionalInfo model.

        :return: nutritional info schema
        """
        return {
            "type": "object",
            "properties": {
                "recipe_id": {
                    "type": "number",
                    **({"default": default_recipe_id} if default_recipe_id is not None else {})
                },
                "calories": {"type": "number", "minimum": 0},
                "protein": {"type": "number", "minimum": 0},
                "carbs": {"type": "number", "minimum": 0},
                "fat": {"type": "number", "minimum": 0},
            },
            "required": ["recipe_id", "calories", "protein", "carbs", "fat"],
            "additionalProperties": False,
        }

    def serialize(self):
        """
        Serialize the NutritionalInfo object to a dictionary.

        :return: Dictionary containing nutritional_info_id, recipe_id, calories, protein, carbs, and fat.
        """
        from food_manager.builder import FoodManagerBuilder

        data = FoodManagerBuilder(
            nutritional_info_id=self.nutritional_info_id,
            recipe_id=self.recipe_id,
            calories=self.calories,
            protein=self.protein,
            carbs=self.carbs,
            fat=self.fat
        )

        data.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        data.add_control("self", href=url_for("api.nutritionalinforesource", nutritional_info_id=self))
        data.add_control("profile", href=NUTRITION_PROFILE)
        data.add_control("collection", href=url_for("api.nutritionalinfolistresource"))
        data.add_control("up", href=url_for("api.reciperesource", recipe_id=self))
        data.add_control_edit_nutritional_info(nutritional_info=self, recipe_id=self.recipe_id)
        data.add_control_delete_nutritional_info(self)

        return data

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

    @staticmethod
    def get_schema() -> dict:
        """Schema for the RecipeIngredient model.

        :return: Recipe_ingredient schema
        """
        return {
            "type": "object",
            "properties": {
                "recipe_id": {"type": "number"},
                "ingredient_id": {"type": "number"},
                "quantity": {"type": "number", "minimum": 0.000001},
                "unit": {"type": "string"},
            },
            "required": ["recipe_id", "ingredient_id", "quantity", "unit"],
            "additionalProperties": False,
        }

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

    @staticmethod
    def get_schema() -> dict:
        """Schema for the RecipeCategory model.

        :return: Recipe_category schema
        """
        return {
            "type": "object",
            "properties": {
                "recipe_id": {"type": "number"},
                "category_id": {"type": "number"},
            },
            "required": ["recipe_id", "category_id"],
            "additionalProperties": False,
        }

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
