"""
Module for Ingredient API endpoints.

This module defines resources for handling ingredients including retrieving,
creating, updating, and deleting them.
"""

from flask import request
from flask_restful import Resource
from flasgger import swag_from
from food_manager.db_operations import (
    create_ingredient,
    get_ingredient_by_id,
    get_all_ingredients,
    update_ingredient,
    delete_ingredient,
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# Ingredient Resources
@class_cache
class IngredientListResource(Resource, ResourceMixin):
    
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
        Handle GET requests to retrieve all ingredient items.
        :return: A JSON response containing a list of serialized ingredient objects,
                 or an error message.
        """
        return self.handle_get_all(get_all_ingredients)

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
        Handle POST requests to create a new ingredient.
        :return: A JSON response with the serialized newly created ingredient object,
                 or an error message.
        """
        return self.handle_create(create_ingredient, request.get_json())


@class_cache
class IngredientResource(Resource, ResourceMixin):

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
        Handle GET requests to retrieve a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to retrieve.
        :return: A JSON response with the serialized ingredient object, or an error
                 message if not found.
        """
        return self.handle_get_by_id(get_ingredient_by_id, ingredient_id)

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
        Handle PUT requests to update an existing ingredient.
        :param ingredient_id: The ID of the ingredient to update.
        :return: A JSON response with the serialized updated ingredient object,
                 or an error message.
        """
        return self.handle_update(update_ingredient, ingredient_id)

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
        Handle DELETE requests to remove a specific ingredient by its ID.
        :param ingredient_id: The ID of the ingredient to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is
                 successful, or an error message.
        """
        return self.handle_delete(delete_ingredient, ingredient_id)