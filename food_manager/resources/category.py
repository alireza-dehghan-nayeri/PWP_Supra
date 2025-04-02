"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""

from flask_restful import Resource, request
from flasgger import swag_from
from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category,
    delete_category
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache


# Category Resources
@class_cache
class CategoryListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of categories.
    This includes retrieving all categories (GET) and creating a new category (POST).
    """

    @swag_from({
        'tags': ['Category'],
        'description': 'Get all categories',
        'responses': {
            200: {
                'description': 'A list of all categories',
                'examples': {
                    'application/json': [
                        {
                            'category_id': 1,
                            'name': 'Italian',
                            'description': 'Italian cuisine'
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
        Handle GET requests to retrieve all categories.
        :return: A JSON response with a list of serialized category objects or an error
                 message.
        """
        return self.handle_get_all(get_all_categories)

    @swag_from({
        'tags': ['Category'],
        'description': 'Create a new category',
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
                            'example': 'Mexican',
                            'description': 'Name of the category'
                        },
                        'description': {
                            'type': 'string',
                            'example': 'Mexican cuisine',
                            'description': 'Description of the category'
                        }
                    },
                    'required': ['name']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'The created category',
                'examples': {
                    'application/json': {
                        'category_id': 2,
                        'name': 'Mexican',
                        'description': 'Mexican cuisine'
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
        Handle POST requests to create a new category.
        :return: A JSON response with the serialized new category or an error message.
        """
        return self.handle_create(create_category, request.get_json())


@class_cache
class CategoryResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single category.
    This includes retrieving, updating, and deleting a category by its ID.
    """

    @swag_from({
        'tags': ['Category'],
        'description': 'Get a specific category by ID',
        'parameters': [
            {
                'name': 'category_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the category to retrieve'
            }
        ],
        'responses': {
            200: {
                'description': 'The requested category',
                'examples': {
                    'application/json': {
                        'category_id': 1,
                        'name': 'Italian',
                        'description': 'Italian cuisine'
                    }
                }
            },
            404: {
                'description': 'Category not found',
                'examples': {
                    'application/json': {
                        'error': 'Category not found'
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, category_id):
        """
        Handle GET requests to retrieve a specific category by its ID.
        :param category_id: The ID of the category to retrieve.
        :return: A JSON response with the serialized category object, or an error
                 message if not found.
        """
        return self.handle_get_by_id(get_category_by_id, category_id, "Category not found")

    @swag_from({
        'tags': ['Category'],
        'description': 'Update an existing category',
        'parameters': [
            {
                'name': 'category_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the category to update'
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
                            'example': 'Updated Italian',
                            'description': 'Updated name of the category'
                        },
                        'description': {
                            'type': 'string',
                            'example': 'Updated Italian cuisine',
                            'description': 'Updated description of the category'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'The updated category',
                'examples': {
                    'application/json': {
                        'category_id': 1,
                        'name': 'Updated Italian',
                        'description': 'Updated Italian cuisine'
                    }
                }
            },
            404: {
                'description': 'Category not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def put(self, category_id):
        """
        Handle PUT requests to update an existing category.
        :param category_id: The ID of the category to update.
        :return: A JSON response with the serialized updated category or an error message.
        """
        return self.handle_update(update_category, category_id, request.json)

    @swag_from({
        'tags': ['Category'],
        'description': 'Delete a specific category',
        'parameters': [
            {
                'name': 'category_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the category to delete'
            }
        ],
        'responses': {
            204: {
                'description': 'Category deleted successfully'
            },
            404: {
                'description': 'Category not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, category_id):
        """
        Handle DELETE requests to remove a specific category by its ID.
        :param category_id: The ID of the category to delete.
        :return: An empty response with status 204 on success or an error message.
        """
        return self.handle_delete(delete_category, category_id)