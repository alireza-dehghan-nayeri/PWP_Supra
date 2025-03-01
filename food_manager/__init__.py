import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Import models after initializing db
db = SQLAlchemy()

from food_manager import models
from food_manager import api
from food_manager.converters.food import FoodConverter
from food_manager.converters.recipe import RecipeConverter
from food_manager.converters.ingredient import IngredientConverter
from food_manager.converters.category import CategoryConverter
from food_manager.converters.nutritional_info import NutritionalInfoConverter

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="supra",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
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
    
    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.sample_data_command)
    app.cli.add_command(models.clear_db_command)
    
    app.url_map.converters['food'] = FoodConverter
    app.url_map.converters['category'] = CategoryConverter
    app.url_map.converters['recipe'] = RecipeConverter
    app.url_map.converters['ingredient'] = IngredientConverter
    app.url_map.converters['nutritional_info'] = NutritionalInfoConverter


    app.register_blueprint(api.api_bp)

    with app.app_context():  # Create tables inside the app context
        db.create_all()

    return app



