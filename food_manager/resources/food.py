"""
Food API Resource Module with Hypermedia (MASON) Support

Provides RESTful endpoints for listing, creating, retrieving, updating,
and deleting food items, enriched with MASON hypermedia controls.
"""

import json
from flask import request, url_for, Response
from flask_restful import Resource
from flasgger import swag_from

from food_manager.db_operations import (
    create_food, get_food_by_id, get_all_foods, update_food, delete_food
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache
from food_manager.constants import MASON, NAMESPACE, LINK_RELATIONS_URL
from food_manager.builder import FoodManagerBuilder


@class_cache
class FoodListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of food items with MASON hypermedia.
    """

    @swag_from({
        'tags': ['Food'],
        'description': 'Get all food items',
        'responses': {
            200: {
                'description': 'A list of all food items',
                'examples': {
                    'application/json': [
                        {
                            'food_id': 1,
                            'name': 'Pizza',
                            'description': 'Italian dish',
                            'image_url': 'http://example.com/pizza.jpg'
                        }
                    ]
                }
            },
            500: {'description': 'Internal server error'}
        }
    })
    def get(self):
        foods = get_all_foods()
        body = FoodManagerBuilder(foods=[])
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.foodlistresource"))
        body.add_control_profile()
        body.add_control_add_food()

        for food in foods:
            entry = FoodManagerBuilder(food.serialize())
            entry.add_control("self", url_for("api.foodresource", food_id=food.food_id))
            entry.add_control("profile", f"{LINK_RELATIONS_URL}/food")
            body["foods"].append(entry)

        return Response(json.dumps(body), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Food'],
        'description': 'Create a new food item',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'example': 'Burger'},
                        'description': {'type': 'string', 'example': 'Fast food'},
                        'image_url': {'type': 'string', 'example': 'http://example.com/burger.jpg'}
                    },
                    'required': ['name']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'The created food item',
                'examples': {
                    'application/json': {
                        'food_id': 2,
                        'name': 'Burger',
                        'description': 'Fast food',
                        'image_url': 'http://example.com/burger.jpg'
                    }
                }
            },
            400: {'description': 'Invalid input'},
            500: {'description': 'Internal server error'}
        }
    })
    def post(self):
        data = request.get_json()
        food = create_food(data)
        builder = FoodManagerBuilder(food.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.foodresource", food_id=food.food_id))
        builder.add_control_profile()
        builder.add_control_all_foods()
        return Response(json.dumps(builder), 201, mimetype=MASON)


@class_cache
class FoodResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single food item with MASON hypermedia.
    """

    @swag_from({
        'tags': ['Food'],
        'description': 'Get a specific food item by ID',
        'parameters': [
            {'name': 'food_id', 'in': 'path', 'type': 'integer', 'required': True}
        ],
        'responses': {
            200: {
                'description': 'The requested food item',
                'examples': {
                    'application/json': {
                        'food_id': 1,
                        'name': 'Pizza',
                        'description': 'Italian dish',
                        'image_url': 'http://example.com/pizza.jpg'
                    }
                }
            },
            404: {'description': 'Food not found'}
        }
    })
    def get(self, food_id):
        food = get_food_by_id(food_id)
        if not food:
            builder = FoodManagerBuilder()
            builder.add_error("Food not found", f"No food with ID {food_id} exists.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(food.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        self_url = url_for("api.foodresource", food_id=food_id)
        builder.add_control("self", self_url)
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/food")
        builder.add_control("collection", url_for("api.foodlistresource"))
        builder.add_control_put("Edit this food", self_url, {
            "name": "string",
            "description": "string",
            "image_url": "string"
        })
        builder.add_control_delete("Delete this food", self_url)
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Food'],
        'description': 'Update an existing food item',
        'parameters': [
            {'name': 'food_id', 'in': 'path', 'type': 'integer', 'required': True},
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'description': {'type': 'string'},
                        'image_url': {'type': 'string'}
                    }
                }
            }
        ],
        'responses': {
            200: {'description': 'Updated food item'},
            404: {'description': 'Food not found'}
        }
    })
    def put(self, food_id):
        data = request.get_json()
        updated = update_food(food_id, data)
        if not updated:
            builder = FoodManagerBuilder()
            builder.add_error("Food not found", f"No food with ID {food_id} exists to update.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(updated.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.foodresource", food_id=food_id))
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/food")
        builder.add_control("collection", url_for("api.foodlistresource"))
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Food'],
        'description': 'Delete a specific food item',
        'parameters': [
            {'name': 'food_id', 'in': 'path', 'type': 'integer', 'required': True}
        ],
        'responses': {
            204: {'description': 'Food deleted'},
            404: {'description': 'Food not found'}
        }
    })
    def delete(self, food_id):
        success = delete_food(food_id)
        if not success:
            builder = FoodManagerBuilder()
            builder.add_error("Food not found", f"No food with ID {food_id} exists to delete.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        return Response(status=204)