"""
Module for Food API endpoints.

This module defines resources for handling food items including
retrieving, creating, updating, and deleting them.
"""

import json
from flask import request
from flask_restful import Resource
from flasgger import swag_from

from food_manager.db_operations import (
    create_food, get_food_by_id, get_all_foods, update_food, delete_food
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# Food Resources
@class_cache
class FoodListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of food items.
    This includes retrieving all food items (GET) and creating a new food item (POST).
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
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self):
        """
        Handle GET requests to retrieve all food items.
        :return: A JSON response containing a list of serialized food objects with
                 HTTP status code 200.
        """
        return self.handle_get_all(get_all_foods)

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
                        'name': {
                            'type': 'string',
                            'example': 'Burger'
                        },
                        'description': {
                            'type': 'string',
                            'example': 'American fast food'
                        },
                        'image_url': {
                            'type': 'string',
                            'example': 'http://example.com/burger.jpg'
                        }
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
                        'description': 'American fast food',
                        'image_url': 'http://example.com/burger.jpg'
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
        Handle POST requests to create a new food item.
        :return: A JSON response with the serialized new food object, or an error
                 message if creation fails.
        """
        return self.handle_create(create_food, request.get_json())


@class_cache
class FoodResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single food item.
    This includes retrieving, updating, and deleting a food item by its unique ID.
    """

    @swag_from({
        'tags': ['Food'],
        'description': 'Get a specific food item by ID',
        'parameters': [
            {
                'name': 'food_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the food item to retrieve'
            }
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
            404: {
                'description': 'Food item not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, food_id):
        """
        Handle GET requests to retrieve a specific food item by its ID.
        :param food_id: The unique identifier of the food item.
        :return: A JSON response with the serialized food object if found, or
                 an error message with HTTP status code 404.
        """
        return self.handle_get_by_id(get_food_by_id, food_id)

    @swag_from({
        'tags': ['Food'],
        'description': 'Update an existing food item',
        'parameters': [
            {
                'name': 'food_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the food item to update'
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
                            'example': 'Updated Pizza'
                        },
                        'description': {
                            'type': 'string',
                            'example': 'Updated Italian dish'
                        },
                        'image_url': {
                            'type': 'string',
                            'example': 'http://example.com/new-pizza.jpg'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'The updated food item',
                'examples': {
                    'application/json': {
                        'food_id': 1,
                        'name': 'Updated Pizza',
                        'description': 'Updated Italian dish',
                        'image_url': 'http://example.com/new-pizza.jpg'
                    }
                }
            },
            404: {
                'description': 'Food item not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def put(self, food_id):
        """
        Handle PUT requests to update an existing food item.
        :param food_id: The unique identifier of the food item to update.
        :return: A JSON response with the serialized updated food object and
                 HTTP status code 200.
        """
        return self.handle_update(update_food, food_id)

    @swag_from({
        'tags': ['Food'],
        'description': 'Delete a specific food item',
        'parameters': [
            {
                'name': 'food_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the food item to delete'
            }
        ],
        'responses': {
            204: {
                'description': 'Food item deleted successfully'
            },
            404: {
                'description': 'Food item not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, food_id):
        """
        Handle DELETE requests to remove a specific food item by its ID.
        :param food_id: The unique identifier of the food item to delete.
        :return: A response indicating that the food item was deleted, with
                    HTTP status code 204 (No Content).
        """
        return self.handle_delete(delete_food, food_id)