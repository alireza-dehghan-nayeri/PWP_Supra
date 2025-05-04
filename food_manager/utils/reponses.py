"""
Utility functions and mixins for API resource handlers.

This module provides reusable functions and mixins to reduce code duplication
across resource handlers.
"""

import json
from flask import Response, json, request

from food_manager.builder import MasonBuilder
from food_manager.constants import MASON, ERROR_PROFILE


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
        mimetype=MASON
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
        mimetype=MASON
    )


def error_response(title, message=None, status_code=400):
    """
    Create an error response with the given message and status code.
    
    :param title: Error title
    :param message: Error message
    :param status_code: HTTP status code for the response
    :return: Flask Response object
    """
    resource_url = request.path
    data = MasonBuilder(resource_url=resource_url)
    data.add_error(title, message)
    data.add_control("profile", href=ERROR_PROFILE)
    return create_json_response(data, status_code)


def handle_request_data():
    """
    Extract JSON data from the request.
    
    :return: Dictionary containing request data
    """
    return request.get_json()
