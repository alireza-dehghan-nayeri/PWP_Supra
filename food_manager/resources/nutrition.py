from flask import Response, json
from flask import request, jsonify
from flask_restful import Resource
from food_manager.db_operations import *

# NutritionalInfo Resources
class NutritionalInfoListResource(Resource):
    def get(self):
        try:
            nutritional_infos = get_all_nutritions()  # Assuming this returns a list of NutritionalInfo objects
            return Response(json.dumps([nutritional_info.serialize() for nutritional_info in nutritional_infos]), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def post(self):
        data = request.get_json()
        try:
            nutritional_info = create_nutritional_info(**data)  # Assuming this creates and returns a NutritionalInfo object
            return Response(json.dumps(nutritional_info.serialize()), 201, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

class NutritionalInfoResource(Resource):
    def get(self, nutritional_info_id):
        try:
            nutritional_info = get_nutritional_info_by_id(nutritional_info_id)  # Assuming this returns a NutritionalInfo object
            if nutritional_info:
                return Response(json.dumps(nutritional_info.serialize()), 200, mimetype="application/json")
            else:
                return Response(json.dumps({"error": "Nutritional Info not found"}), 404, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def put(self, nutritional_info_id):
        data = request.get_json()
        try:
            nutritional_info = update_nutritional_info(nutritional_info_id, **data)  # Assuming this returns an updated NutritionalInfo object
            return Response(json.dumps(nutritional_info.serialize()), 200, mimetype="application/json")
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")

    def delete(self, nutritional_info_id):
        try:
            delete_nutritional_info(nutritional_info_id)  # Assuming this deletes the nutritional info from DB
            return Response("", 204)  # No content response
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), 500, mimetype="application/json")
