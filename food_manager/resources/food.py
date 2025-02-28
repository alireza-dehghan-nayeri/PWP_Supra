import json

from flask import request, jsonify, Response
from flask_restful import Resource
from food_manager.db_operations import (
    create_food, get_food_by_id, get_all_foods, update_food, delete_food
    )

# Food Resources
class FoodListResource(Resource):
    def get(self):
        # Get all foods and serialize them
        foods = [food.serialize() for food in get_all_foods()]
        return Response(json.dumps(foods), 200, mimetype="application/json")

    def post(self):
        data = request.get_json()
        try:
            food = create_food(**data)
            return Response(json.dumps(food.serialize()), 201, mimetype="application/json")  # Return dictionary serialized to JSON
        except ValueError as e:
            return Response(json.dumps({"error": str(e)}), 400, mimetype="application/json")  # Error response
        except Exception as e:
            return Response(json.dumps({"error": "An unexpected error occurred.", "details": str(e)}), 500, mimetype="application/json")  # Error response

class FoodResource(Resource):
    def get(self, food_id):
        food = get_food_by_id(food_id)
        if food:
            return Response(json.dumps(food.serialize()), 200, mimetype="application/json")
        else:
            return Response(json.dumps({"error": "Food not found"}), 404, mimetype="application/json")

    def put(self, food_id):
        data = request.get_json()
        food = update_food(food_id, **data)
        return Response(json.dumps(food.serialize()), 200, mimetype="application/json")

    def delete(self, food_id):
        delete_food(food_id)
        return Response("Food Item Deleted", 204, mimetype="application/json")
