from flask import Response, json
from flask import request, jsonify
from flask_restful import Resource
from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category, delete_category
    )

# Category Resources
class CategoryListResource(Resource):
    def get(self):
        try:
            categories = get_all_categories()  # Assuming this returns a list of Category objects
            return Response(json.dumps([category.serialize() for category in categories]), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def post(self):
        data = request.get_json()
        try:
            category = create_category(**data)  # Assuming this creates and returns a Category object
            return Response(json.dumps(category.serialize()), 201, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

class CategoryResource(Resource):
    def get(self, category_id):
        try:
            category = get_category_by_id(category_id)  # Assuming this returns a Category object
            if category:
                return Response(json.dumps(category.serialize()), 200, mimetype="application/json")
            else:
                return Response(json.dumps({"error": "Category not found"}), 404, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def put(self, category_id):
        data = request.get_json()
        try:
            category = update_category(category_id, **data)  # Assuming this returns an updated Category object
            return Response(json.dumps(category.serialize()), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, category_id):
        try:
            delete_category(category_id)  # Assuming this deletes the category from DB
            return Response("", 204)  # No content response
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
