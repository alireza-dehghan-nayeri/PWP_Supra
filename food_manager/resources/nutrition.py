"""
Nutrition API Resource Module with Hypermedia (MASON) Support

Provides RESTful endpoints for listing, creating, retrieving, updating,
and deleting nutritional information items, enriched with MASON hypermedia controls.
"""

import json
from flask import request, url_for, Response
from flask_restful import Resource
from flasgger import swag_from

from food_manager.db_operations import (
    create_nutritional_info, get_all_nutritions, get_nutritional_info_by_id,
    update_nutritional_info, delete_nutritional_info
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache
from food_manager.constants import MASON, NAMESPACE, LINK_RELATIONS_URL
from food_manager.builder import FoodManagerBuilder


@class_cache
class NutritionalInfoListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of nutritional information items.
    """

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Get all nutritional information items',
        'responses': {
            200: {
                'description': 'A list of all nutritional information items',
                'examples': {
                    'application/json': [
                        {
                            "nutritional_info_id": 1,
                            "recipe_id": 1,
                            "calories": 500,
                            "protein": 20.5,
                            "carbs": 60.2,
                            "fat": 15.3
                        }
                    ]
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self):
        """
        Handle GET requests to retrieve all nutritional information items with hypermedia.
        """
        nutritions = get_all_nutritions()
        body = FoodManagerBuilder(nutritions=[])
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.nutritioninfolistresource"))
        body.add_control_profile()
        body.add_control_add_nutritional_info()

        for item in nutritions:
            entry = FoodManagerBuilder(item.serialize())
            entry.add_control("self", url_for("api.nutritioninforesource", nutritional_info_id=item.nutritional_info_id))
            entry.add_control("profile", f"{LINK_RELATIONS_URL}/nutrition")
            body["nutritions"].append(entry)

        return Response(json.dumps(body), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Create new nutritional information',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'recipe_id': {'type': 'integer', 'example': 1},
                        'calories': {'type': 'integer', 'example': 500},
                        'protein': {'type': 'number', 'format': 'float', 'example': 20.5},
                        'carbs': {'type': 'number', 'format': 'float', 'example': 60.2},
                        'fat': {'type': 'number', 'format': 'float', 'example': 15.3}
                    },
                    'required': ['recipe_id', 'calories', 'protein', 'carbs', 'fat']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'The created nutritional information',
                'examples': {
                    'application/json': {
                        "nutritional_info_id": 2,
                        "recipe_id": 2,
                        "calories": 350,
                        "protein": 15.0,
                        "carbs": 45.0,
                        "fat": 10.0
                    }
                }
            },
            400: {'description': 'Invalid input'},
            500: {'description': 'Internal server error'}
        }
    })
    def post(self):
        """
        Handle POST requests to create a new nutritional information item with hypermedia.
        """
        data = request.get_json()
        nutrition = create_nutritional_info(data)
        builder = FoodManagerBuilder(nutrition.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.nutritioninforesource", nutritional_info_id=nutrition.nutritional_info_id))
        builder.add_control_profile()
        builder.add_control_all_nutritional_info()
        return Response(json.dumps(builder), 201, mimetype=MASON)


@class_cache
class NutritionalInfoResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single nutritional information item.
    """

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Get specific nutritional information by ID',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True
            }
        ],
        'responses': {
            200: {
                'description': 'The requested nutritional information',
                'examples': {
                    'application/json': {
                        "nutritional_info_id": 1,
                        "recipe_id": 1,
                        "calories": 500,
                        "protein": 20.5,
                        "carbs": 60.2,
                        "fat": 15.3
                    }
                }
            },
            404: {
                'description': 'Nutritional information not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, nutritional_info_id):
        """
        Handle GET requests to retrieve a specific nutritional info item by ID with hypermedia.
        """
        nutrition = get_nutritional_info_by_id(nutritional_info_id)
        if not nutrition:
            builder = FoodManagerBuilder()
            builder.add_error("Nutrition info not found", f"No item with ID {nutritional_info_id} exists.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(nutrition.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        self_url = url_for("api.nutritioninforesource", nutritional_info_id=nutritional_info_id)
        builder.add_control("self", self_url)
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/nutrition")
        builder.add_control("collection", url_for("api.nutritioninfolistresource"))
        builder.add_control_put("Edit this nutrition info", self_url, {
            "calories": "integer",
            "protein": "float",
            "carbs": "float",
            "fat": "float"
        })
        builder.add_control_delete("Delete this nutrition info", self_url)
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Update existing nutritional information',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'calories': {'type': 'integer', 'example': 450},
                        'protein': {'type': 'number', 'format': 'float', 'example': 18.0},
                        'carbs': {'type': 'number', 'format': 'float', 'example': 55.0},
                        'fat': {'type': 'number', 'format': 'float', 'example': 12.0}
                    }
                }
            }
        ],
        'responses': {
            200: {'description': 'Updated nutritional info'},
            404: {'description': 'Nutritional info not found'}
        }
    })
    def put(self, nutritional_info_id):
        """
        Handle PUT requests to update an existing nutritional info item with hypermedia.
        """
        data = request.get_json()
        updated = update_nutritional_info(nutritional_info_id, data)
        if not updated:
            builder = FoodManagerBuilder()
            builder.add_error("Nutrition info not found", f"No item with ID {nutritional_info_id} exists to update.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(updated.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.nutritioninforesource", nutritional_info_id=nutritional_info_id))
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/nutrition")
        builder.add_control("collection", url_for("api.nutritioninfolistresource"))
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Delete specific nutritional information',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True
            }
        ],
        'responses': {
            204: {'description': 'Deleted'},
            404: {'description': 'Not found'}
        }
    })
    def delete(self, nutritional_info_id):
        """
        Handle DELETE requests to remove a specific nutritional info item by its ID with hypermedia.
        """
        success = delete_nutritional_info(nutritional_info_id)
        if not success:
            builder = FoodManagerBuilder()
            builder.add_error("Nutrition info not found", f"No item with ID {nutritional_info_id} exists to delete.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        return Response(status=204)
