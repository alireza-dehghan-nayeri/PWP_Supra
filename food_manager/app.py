from flask import Flask
from food_manager.config import Config
from food_manager.models import db, init_app
from food_manager.api import api_bp
from food_manager.converters.food import FoodConverter
from food_manager.converters.recipe import RecipeConverter
from food_manager.converters.ingredient import IngredientConverter
from food_manager.converters.category import CategoryConverter
from food_manager.converters.nutritional_info import NutritionalInfoConverter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    init_app(app)
    
    with app.app_context():  # Create tables inside the app context
        db.create_all()
        
    # Register custom converter for 'food_id' to Food object
    app.url_map.converters['food'] = FoodConverter
    app.url_map.converters['category'] = CategoryConverter
    app.url_map.converters['recipe'] = RecipeConverter
    app.url_map.converters['ingredient'] = IngredientConverter
    app.url_map.converters['nutritional_info'] = NutritionalInfoConverter

    # Register the API blueprint
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    