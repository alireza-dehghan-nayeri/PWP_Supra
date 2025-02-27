from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import *

db = SQLAlchemy()

class Food(db.Model):
    __tablename__ = 'food'
    
    name = db.Column(db.String(64), primary_key=True)
    description = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    # Relationships
    recipes = db.relationship('Recipe', back_populates='food', lazy='dynamic')

    def __repr__(self):
        return f'<Food {self.name}>'

    def serialize(self):
        return {
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
    
    name = db.Column(db.String(64), primary_key=True)
    food_name = db.Column(db.String(64), db.ForeignKey('food.name'), nullable=False)
    instruction = db.Column(db.String(255), nullable=False)
    prep_time = db.Column(db.Integer, nullable=False)
    cook_time = db.Column(db.Integer, nullable=False)
    servings = db.Column(db.Integer, nullable=False, default=1)
    
    # Relationships
    food = db.relationship('Food', back_populates='recipes')
    nutritional_info = db.relationship('NutritionalInfo', back_populates='recipe', uselist=False)
    
    # Many-to-many relationships without explicit junction models
    ingredients = db.relationship(
        'Ingredient',
        secondary='recipe_ingredient',
        backref=db.backref('recipes', lazy='dynamic')
    )
    
    categories = db.relationship(
        'Category',
        secondary='recipe_category',
        backref=db.backref('recipes', lazy='dynamic')
    )

    def __repr__(self):
        return f'<Recipe {self.name}>'

    def serialize(self):
        # Get ingredient quantities from the junction table
        ingredient_data = []
        for ingredient in self.ingredients:
            junction = db.session.query(
                db.metadata.tables['recipe_ingredient']
            ).filter_by(
                recipe_name=self.name,
                ingredient_name=ingredient.name
            ).first()
            
            if junction:
                ingredient_data.append({
                    'ingredient': ingredient.serialize(),
                    'quantity': junction.quantity,
                    'unit': junction.unit
                })
            else:
                ingredient_data.append({
                    'ingredient': ingredient.serialize(),
                    'quantity': None,
                    'unit': None
                })
                
        return {
            'name': self.name,
            'food_name': self.food_name,
            'instruction': self.instruction,
            'prep_time': self.prep_time,
            'cook_time': self.cook_time,
            'servings': self.servings,
            'food': self.food.serialize(),
            'nutritional_info': self.nutritional_info.serialize() if self.nutritional_info else None,
            'ingredients': ingredient_data,
            'categories': [cat.serialize() for cat in self.categories]
        }

    @staticmethod
    def deserialize(data):
        return Recipe(
            name=data.get('name'),
            food_name=data.get('food_name'),
            instruction=data.get('instruction'),
            prep_time=data.get('prep_time'),
            cook_time=data.get('cook_time'),
            servings=data.get('servings')
        )

class Ingredient(db.Model):
    __tablename__ = 'ingredient'
    
    name = db.Column(db.String(64), primary_key=True)
    image_url = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Ingredient {self.name}>'

    def serialize(self):
        return {
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
    
    name = db.Column(db.String(64), primary_key=True)
    description = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'

    def serialize(self):
        return {
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
    
    recipe_name = db.Column(db.String(64), db.ForeignKey('recipe.name'), primary_key=True)
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carbs = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='nutritional_info')

    def __repr__(self):
        return f'<NutritionalInfo for recipe {self.recipe_name}>'

    def serialize(self):
        return {
            'recipe_name': self.recipe_name,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat
        }

    @staticmethod
    def deserialize(data):
        return NutritionalInfo(
            recipe_name=data.get('recipe_name'),
            calories=data.get('calories'),
            protein=data.get('protein'),
            carbs=data.get('carbs'),
            fat=data.get('fat')
        )

# Junction tables (without models)
recipe_ingredient = db.Table('recipe_ingredient',
    db.Column('recipe_name', db.String(64), db.ForeignKey('recipe.name'), primary_key=True),
    db.Column('ingredient_name', db.String(64), db.ForeignKey('ingredient.name'), primary_key=True),
    db.Column('quantity', db.Float, nullable=False, default=1),
    db.Column('unit', db.String(64), nullable=True, default='piece')
)

recipe_category = db.Table('recipe_category',
    db.Column('recipe_name', db.String(64), db.ForeignKey('recipe.name'), primary_key=True),
    db.Column('category_name', db.String(64), db.ForeignKey('category.name'), primary_key=True)
)
