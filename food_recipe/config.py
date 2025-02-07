import os

class Config:
    # Database configuration
    SECRET_KEY = "supra"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
