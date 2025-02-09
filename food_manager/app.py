from flask import Flask
from config import Config
from db_init import init_app
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    init_app(app)
    
    with app.app_context():  # Create tables inside the app context
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)