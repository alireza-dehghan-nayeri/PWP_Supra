"""Main application module for Food Manager.

This module creates and configures the Flask application using settings defined
in the configuration, initializes the database, and runs the application.
"""

from flask import Flask
from .config import Config
from .models import db, init_app


def create_app():
    """
    Create and configure the Flask application.

    This function configures the application from the Config class,
    initializes the SQLAlchemy database, and registers CLI commands. It also
    creates all database tables within the application context.

    :return: A configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the database and register any CLI commands.
    db.init_app(app)
    init_app(app)

    with app.app_context():
        # Create all database tables.
        db.create_all()

    return app


if __name__ == '__main__':
    # Create the application instance and run the Flask development server.
    application = create_app()
    application.run(debug=True)
