"""
Utility functions and mixins for API resource handlers.

This module provides reusable functions and mixins to reduce code duplication
across resource handlers.
"""

import json
from flask import Response, json, request

def internal_server_error(error: Exception) -> Response:
    """
    Handle internal server errors and return a JSON response.

    Args:
        error (Exception): The exception that was raised.

    Returns:
        Response: A Flask Response object containing the error details in JSON format.
    """
    return Response(
        json.dumps({
            "error": "An unexpected error occurred.",
            "details": str(error)
        }),
        status=500,
        mimetype="application/json"
    )

def create_json_response(data, status_code=200):
    """
    Create a Flask Response with JSON data.
    
    :param data: The data to be converted to JSON
    :param status_code: HTTP status code for the response
    :return: Flask Response object
    """
    return Response(
        json.dumps(data),
        status_code,
        mimetype="application/json"
    )


def error_response(message, status_code=400):
    """
    Create an error response with the given message and status code.
    
    :param message: Error message
    :param status_code: HTTP status code for the response
    :return: Flask Response object
    """
    return create_json_response({"error": message}, status_code)


def handle_request_data():
    """
    Extract JSON data from the request.
    
    :return: Dictionary containing request data
    """
    return request.get_json()


class ResourceMixin:
    """
    Mixin class providing common resource handler methods.
    """
    
    def handle_get_all(self, get_all_func):
        """
        Handle GET requests to retrieve all items.
        
        :param get_all_func: Function to retrieve all items
        :return: JSON response with serialized items
        """
        try:
            items = get_all_func()
            serialized_items = [item.serialize() for item in items]
            return create_json_response(serialized_items)
        except Exception as e:
            return internal_server_error(e)
    
    def handle_get_by_id(self, get_by_id_func, item_id, not_found_message=None):
        """
        Handle GET requests to retrieve a specific item by ID.
        
        :param get_by_id_func: Function to retrieve item by ID
        :param item_id: ID of the item to retrieve
        :param not_found_message: Custom message when item is not found
        :return: JSON response with serialized item or error
        """
        try:
            item = get_by_id_func(item_id)
            if item:
                return create_json_response(item.serialize())
            
            message = not_found_message or "Item not found"
            return error_response(message, 404)
        except Exception as e:
            return internal_server_error(e)
    
    def handle_create(self, create_func, data=None):
        """
        Handle POST requests to create a new item.
        
        :param create_func: Function to create item
        :param data: Request data (if None, will be extracted from request)
        :return: JSON response with created item
        """
        if data is None:
            data = handle_request_data()
        try:
            item = create_func(**data)
            return create_json_response(item.serialize(), 201)
        except ValueError as e:
            return error_response(str(e), 400)
        except Exception as e:
            return internal_server_error(e)
    
    def handle_update(self, update_func, item_id, data=None):
        """
        Handle PUT requests to update an existing item.
        
        :param update_func: Function to update item
        :param item_id: ID of the item to update
        :param data: Request data (if None, will be extracted from request)
        :return: JSON response with updated item
        """
        if data is None:
            data = handle_request_data()
            
        try:
            item = update_func(item_id, **data)
            return create_json_response(item.serialize())
        except Exception as e:
            return internal_server_error(e)
    
    def handle_delete(self, delete_func, item_id):
        """
        Handle DELETE requests to remove an item.
        
        :param delete_func: Function to delete item
        :param item_id: ID of the item to delete
        :return: Empty response with status 204 or error
        """
        try:
            delete_func(item_id)
            return Response("", 204)
        except Exception as e:
            return internal_server_error(e)