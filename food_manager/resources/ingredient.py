"""
Ingredient API Resource Module with Hypermedia (MASON) Support

Provides RESTful endpoints for listing, creating, retrieving, updating,
and deleting ingredient items, enriched with MASON hypermedia controls.
"""

import json
from flask import request, url_for, Response
from flask_restful import Resource
from flasgger import swag_from

from food_manager.db_operations import (
    create_ingredient, get_ingredient_by_id, get_all_ingredients,
    update_ingredient, delete_ingredient,
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache
from food_manager.constants import MASON, NAMESPACE, LINK_RELATIONS_URL
from food_manager.builder import FoodManagerBuilder


@class_cache
class IngredientListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of ingredient items.
    """

    @swag_from({
        'tags': ['Ingredient'],
        'description': 'Get all ingredient items',
        'responses': {
            200: {
                'description': 'A list of all ingredient items',
                'examples': {
                    'application/json': [
                        {
                            'ingredient_id': 1,
                            'name': 'Flour',
                            'image_url': 'http://example.com/flour.jpg'
                        },
                        {
                            'ingredient_id': 2,
                            'name': 'Sugar',
                            'image_url': 'http://example.com/sugar.jpg'
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
        Handle GET requests to retrieve all ingredient items with hypermedia.
        """
        ingredients = get_all_ingredients()
        body = FoodManagerBuilder(ingredients=[])
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.ingredientlistresource"))
        body.add_control_profile()
        body.add_control_add_ingredient()

        for item in ingredients:
            entry = FoodManagerBuilder(item.serialize())
            entry.add_control("self", url_for("api.ingredientresource", ingredient_id=item.ingredient_id))
            entry.add_control("profile", f"{LINK_RELATIONS_URL}/ingredient")
            body["ingredients"].append(entry)

        return Response(json.dumps(body), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Ingredient'],
        'description': 'Create a new ingredient item',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'example': 'Salt',
                            'description': 'Name of the ingredient'
                        },
                        'image_url': {
                            'type': 'string',
                            'example': 'http://example.com/salt.jpg',
                            'description': 'URL of ingredient image'
                        }
                    },
                    'required': ['name']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'The created ingredient item',
                'examples': {
                    'application/json': {
                        'ingredient_id': 3,
                        'name': 'Salt',
                        'image_url': 'http://example.com/salt.jpg'
                    }
                }
            },
            400: {
                'description': 'Invalid input or missing required fields'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def post(self):
        """
        Handle POST requests to create a new ingredient with hypermedia.
        """
        data = request.get_json()
        ingredient = create_ingredient(data)
        builder = FoodManagerBuilder(ingredient.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.ingredientresource", ingredient_id=ingredient.ingredient_id))
        builder.add_control_profile()
        builder.add_control_all_ingredients()
        return Response(json.dumps(builder), 201, mimetype=MASON)


@class_cache
class IngredientResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single ingredient item.
    """

    @swag_from({
        'tags': ['Ingredient'],
        'description': 'Get a specific ingredient by ID',
        'parameters': [
            {
                'name': 'ingredient_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the ingredient to retrieve'
            }
        ],
        'responses': {
            200: {
                'description': 'The requested ingredient',
                'examples': {
                    'application/json': {
                        'ingredient_id': 1,
                        'name': 'Flour',
                        'image_url': 'http://example.com/flour.jpg'
                    }
                }
            },
            404: {
                'description': 'Ingredient not found',
                'examples': {
                    'application/json': {
                        'error': 'Ingredient not found'
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, ingredient_id):
        """
        Handle GET requests to retrieve a specific ingredient by its ID with hypermedia.
        """
        ingredient = get_ingredient_by_id(ingredient_id)
        if not ingredient:
            builder = FoodManagerBuilder()
            builder.add_error("Ingredient not found", f"No ingredient with ID {ingredient_id} exists.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(ingredient.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        self_url = url_for("api.ingredientresource", ingredient_id=ingredient_id)
        builder.add_control("self", self_url)
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/ingredient")
        builder.add_control("collection", url_for("api.ingredientlistresource"))
        builder.add_control_put("Edit this ingredient", self_url, {
            "name": "string",
            "image_url": "string"
        })
        builder.add_control_delete("Delete this ingredient", self_url)
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Ingredient'],
        'description': 'Update an existing ingredient',
        'parameters': [
            {
                'name': 'ingredient_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the ingredient to update'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'example': 'Whole Wheat Flour',
                            'description': 'Updated name of the ingredient'
                        },
                        'image_url': {
                            'type': 'string',
                            'example': 'http://example.com/whole-wheat-flour.jpg',
                            'description': 'Updated URL of ingredient image'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'The updated ingredient',
                'examples': {
                    'application/json': {
                        'ingredient_id': 1,
                        'name': 'Whole Wheat Flour',
                        'image_url': 'http://example.com/whole-wheat-flour.jpg'
                    }
                }
            },
            404: {
                'description': 'Ingredient not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def put(self, ingredient_id):
        """
        Handle PUT requests to update an existing ingredient with hypermedia.
        """
        data = request.get_json()
        updated = update_ingredient(ingredient_id, data)
        if not updated:
            builder = FoodManagerBuilder()
            builder.add_error("Ingredient not found", f"No ingredient with ID {ingredient_id} exists to update.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(updated.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.ingredientresource", ingredient_id=ingredient_id))
        builder.add_control("profile", f"{LINK_RELATIONS_URL}/ingredient")
        builder.add_control("collection", url_for("api.ingredientlistresource"))
        return Response(json.dumps(builder), 200, mimetype=MASON)

    @swag_from({
        'tags': ['Ingredient'],
        'description': 'Delete a specific ingredient',
        'parameters': [
            {
                'name': 'ingredient_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the ingredient to delete'
            }
        ],
        'responses': {
            204: {
                'description': 'Ingredient deleted successfully'
            },
            404: {
                'description': 'Ingredient not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, ingredient_id):
        """
        Handle DELETE requests to remove a specific ingredient by its ID with hypermedia.
        """
        success = delete_ingredient(ingredient_id)
        if not success:
            builder = FoodManagerBuilder()
            builder.add_error("Ingredient not found", f"No ingredient with ID {ingredient_id} exists to delete.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        return Response(status=204)
