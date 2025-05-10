from food_manager import create_app

def main():
    app = create_app()
    app.run(debug=True)