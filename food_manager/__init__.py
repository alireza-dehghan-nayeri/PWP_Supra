"""Application factory for Food Manager.

This module initializes and configures the Flask application, including the
SQLAlchemy database, caching, CLI commands, and URL converters.
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# Initialize the SQLAlchemy database instance.
db = SQLAlchemy()

# Create a global Cache instance for caching operations.
cache = Cache()

from food_manager import cli
from food_manager import api
from food_manager.converters.food import FoodConverter
from food_manager.converters.recipe import RecipeConverter
from food_manager.converters.ingredient import IngredientConverter
from food_manager.converters.category import CategoryConverter
from food_manager.converters.nutritional_info import NutritionalInfoConverter

def create_app(test_config=None):
    """
    Create and configure the Flask application.

    :param test_config: Optional dictionary with configuration values for testing.
    :return: Configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="supra",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE='simple',
        CACHE_DEFAULT_TIMEOUT=86400
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)

    cli.init_app(app)

    app.url_map.converters['food'] = FoodConverter
    app.url_map.converters['category'] = CategoryConverter
    app.url_map.converters['recipe'] = RecipeConverter
    app.url_map.converters['ingredient'] = IngredientConverter
    app.url_map.converters['nutritional_info'] = NutritionalInfoConverter

    app.register_blueprint(api.api_bp)

    with app.app_context():
        db.create_all()

    return app
