"""
Module for Nutritional Information API endpoints.

This module defines resources for handling nutritional information items.
It supports GET (list and detail), POST, PUT, and DELETE operations.
"""

from flask import Response, json, request
from flask_restful import Resource
from flasgger import swag_from

from food_manager.db_operations import (
    create_nutritional_info, get_all_nutritions, get_nutritional_info_by_id,
    update_nutritional_info, delete_nutritional_info
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# NutritionalInfo Resources
@class_cache
class NutritionalInfoListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of nutritional information items.
    This includes retrieving all nutritional info items (GET) and creating a new 
    nutritional info item (POST).
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
        Handle GET requests to retrieve all nutritional information items.
        :return: A JSON response containing a list of serialized nutritional info
                 objects with HTTP status code 200.
        """
        return self.handle_get_all(get_all_nutritions)

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
                        'recipe_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the associated recipe'
                        },
                        'calories': {
                            'type': 'integer',
                            'example': 500,
                            'description': 'Number of calories'
                        },
                        'protein': {
                            'type': 'number',
                            'format': 'float',
                            'example': 20.5,
                            'description': 'Amount of protein in grams'
                        },
                        'carbs': {
                            'type': 'number',
                            'format': 'float',
                            'example': 60.2,
                            'description': 'Amount of carbohydrates in grams'
                        },
                        'fat': {
                            'type': 'number',
                            'format': 'float',
                            'example': 15.3,
                            'description': 'Amount of fat in grams'
                        }
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
        Handle POST requests to create a new nutritional information item.
        :return: A JSON response with the serialized new nutritional info object or 
                 an error message if creation fails.
        """
        return self.handle_create(create_nutritional_info, request.get_json())


@class_cache
class NutritionalInfoResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single nutritional information item.
    This includes retrieving, updating, and deleting a nutritional info item by its ID.
    """

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Get specific nutritional information by ID',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the nutritional information to retrieve'
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
                'description': 'Nutritional information not found',
                'examples': {
                    'application/json': {
                        'error': 'Nutritional info not found'
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, nutritional_info_id):
        """
        Handle GET requests to retrieve a specific nutritional info item by its ID.
        :param nutritional_info_id: The unique identifier of the nutritional info item.
        :return: A JSON response with the serialized nutritional info object if found,
                 or an error message with HTTP status code 404 if not found.
        """
        return self.handle_get_by_id(get_nutritional_info_by_id, nutritional_info_id)

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Update existing nutritional information',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the nutritional information to update'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'calories': {
                            'type': 'integer',
                            'example': 450,
                            'description': 'Updated number of calories'
                        },
                        'protein': {
                            'type': 'number',
                            'format': 'float',
                            'example': 18.0,
                            'description': 'Updated amount of protein in grams'
                        },
                        'carbs': {
                            'type': 'number',
                            'format': 'float',
                            'example': 55.0,
                            'description': 'Updated amount of carbohydrates in grams'
                        },
                        'fat': {
                            'type': 'number',
                            'format': 'float',
                            'example': 12.0,
                            'description': 'Updated amount of fat in grams'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'The updated nutritional information',
                'examples': {
                    'application/json': {
                        "nutritional_info_id": 1,
                        "recipe_id": 1,
                        "calories": 450,
                        "protein": 18.0,
                        "carbs": 55.0,
                        "fat": 12.0
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
    def put(self, nutritional_info_id):
        """
        Handle PUT requests to update an existing nutritional info item.
        :param nutritional_info_id: The unique identifier of the nutritional info item to update.
        :return: A JSON response with the serialized updated nutritional info object,
                 or an error message if the update fails.
        """
        return self.handle_update(update_nutritional_info, nutritional_info_id)

    @swag_from({
        'tags': ['Nutrition'],
        'description': 'Delete specific nutritional information',
        'parameters': [
            {
                'name': 'nutritional_info_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the nutritional information to delete'
            }
        ],
        'responses': {
            204: {
                'description': 'Nutritional information deleted successfully'
            },
            404: {
                'description': 'Nutritional information not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, nutritional_info_id):
        """
        Handle DELETE requests to remove a specific nutritional info item by its ID.
        :param nutritional_info_id: The unique identifier of the nutritional info item to delete.
        :return: A response with HTTP status code 204 (No Content) if deletion is successful,
                 or an error message if deletion fails.
        """
        return self.handle_delete(delete_nutritional_info, nutritional_info_id)