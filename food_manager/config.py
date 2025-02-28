class Config:
    # Database configuration
    SECRET_KEY = "supra"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///food-manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False