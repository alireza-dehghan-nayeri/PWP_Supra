from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import *


db = SQLAlchemy()

class Food(db.Model):
    __tablename__ = 'food'
    
    food_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    recipes = db.relationship('Recipe', back_populates='food', lazy='dynamic')

    def __repr__(self):
        return f'<Food {self.name}>'

    def serialize(self):
        return {
            'food_id': self.food_id,
            'name': self.name,
            'description': self.description,
            'image_url': self.image_url
        }

    @staticmethod
    def deserialize(data):
        return Food(
            name=data.get('name'),
            description=data.get('description'),
            image_url=data.get('image_url')
        )

class Recipe(db.Model):
    __tablename__ = 'recipe'
    
    recipe_id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.food_id'), nullable=False)
    instruction = db.Column(db.String(255), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    servings = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    food = db.relationship('Food', back_populates='recipes')
    nutritional_info = db.relationship('NutritionalInfo', back_populates='recipe', uselist=False)
    ingredients = db.relationship('Ingredient', secondary='recipe_ingredient', back_populates='recipes')
    categories = db.relationship('Category', secondary='recipe_category', back_populates='recipes')

    def __repr__(self):
        return f'<Recipe {self.recipe_id} for {self.food.name}>'

    def serialize(self):
        return {
            'recipe_id': self.recipe_id,
            'food_id': self.food_id,
            'instruction': self.instruction,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'food': self.food.serialize(),
            'nutritional_info': self.nutritional_info.serialize() if self.nutritional_info else None,
            'ingredients': [{'ingredient': ing.serialize(), 
                           'quantity': next((ri.quantity for ri in self.recipe_ingredients if ri.ingredient_id == ing.ingredient_id), None),
                           'unit': next((ri.unit for ri in self.recipe_ingredients if ri.ingredient_id == ing.ingredient_id), None)}
                          for ing in self.ingredients],
            'categories': [cat.serialize() for cat in self.categories]
        }

    @staticmethod
    def deserialize(data):
        return Recipe(
            food_id=data.get('food_id'),
            instruction=data.get('instruction'),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings')
        )

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    
    ingredient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    recipes = db.relationship('Recipe', secondary='recipe_ingredient', back_populates='ingredients')

    def __repr__(self):
        return f'<Ingredient {self.name}>'

    def serialize(self):
        return {
            'ingredient_id': self.ingredient_id,
            'name': self.name,
            'image_url': self.image_url
        }

    @staticmethod
    def deserialize(data):
        return Ingredient(
            name=data.get('name'),
            image_url=data.get('image_url')
        )

class Category(db.Model):
    __tablename__ = 'category'
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
    # Relationships
    recipes = db.relationship('Recipe', secondary='recipe_category', back_populates='categories')

    def __repr__(self):
        return f'<Category {self.name}>'

    def serialize(self):
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description
        }

    @staticmethod
    def deserialize(data):
        return Category(
            name=data.get('name'),
            description=data.get('description')
        )

class NutritionalInfo(db.Model):
    __tablename__ = 'nutritional_info'
    
    nutritional_info_id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), unique=True, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='nutritional_info')

    def __repr__(self):
        return f'<NutritionalInfo for recipe {self.recipe_id}>'

    def serialize(self):
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
        return NutritionalInfo(
            recipe_id=data.get('recipe_id'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            carbs=data.get('carbs'),
            fat=data.get('fat')
        )

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), primary_key=True)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit = db.Column(db.String(64), nullable=True, default='piece')

    def __repr__(self):
        return f'<RecipeIngredient {self.recipe_id}:{self.ingredient_id}>'

    def serialize(self):
        return {
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'quantity': self.quantity,
            'unit': self.unit
        }

    @staticmethod
    def deserialize(data):
        return RecipeIngredient(
            recipe_id=data.get('recipe_id'),
            ingredient_id=data.get('ingredient_id'),
            quantity=data.get('quantity'),
            unit=data.get('unit')
        )

class RecipeCategory(db.Model):
    __tablename__ = 'recipe_category'
    
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)

    def __repr__(self):
        return f'<RecipeCategory {self.recipe_id}:{self.category_id}>'

    def serialize(self):
        return {
            'recipe_id': self.recipe_id,
            'category_id': self.category_id
        }

    @staticmethod
    def deserialize(data):
        return RecipeCategory(
            recipe_id=data.get('recipe_id'),
            category_id=data.get('category_id')
        )