"""Configuration settings for the Food Manager application."""

class Config:
    """Configuration class for the Food Manager application."""
    # Database configuration
    SECRET_KEY = "supra"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///food-manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
