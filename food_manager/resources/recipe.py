"""
Module for Recipe API endpoints.

This module defines resources for handling recipes and their associations.
"""

from flask import Response, request
import json
from flask_restful import Resource
from flasgger import swag_from
from food_manager.db_operations import (
    create_recipe, get_recipe_by_id, get_all_recipes, update_recipe, delete_recipe,
    add_ingredient_to_recipe, update_recipe_ingredient, remove_ingredient_from_recipe,
    add_category_to_recipe, remove_category_from_recipe
)
from food_manager.utils.reponses import ResourceMixin, internal_server_error
from food_manager.utils.cache import class_cache


# Recipe Resources
@class_cache
class RecipeListResource(Resource, ResourceMixin):
    """
    Resource for handling operations on the list of recipes.
    Supports GET for retrieving all recipes and POST for creating a new recipe.
    """

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Get all recipes',
        'responses': {
            200: {
                'description': 'List of all recipes with full details',
                'examples': {
                    'application/json': [
                        {
                            'recipe_id': 1,
                            'food_id': 1,
                            'instruction': 'Mix ingredients and bake',
                            'prep_time': 30,
                            'cook_time': 45,
                            'servings': 4,
                            'food': {
                                'food_id': 1,
                                'name': 'Pizza',
                                'description': 'Italian dish',
                                'image_url': 'http://example.com/pizza.jpg'
                            },
                            'nutritional_info': {
                                'nutritional_info_id': 1,
                                'recipe_id': 1,
                                'calories': 500,
                                'protein': 20.5,
                                'carbs': 60.2,
                                'fat': 15.3
                            },
                            'ingredients': [
                                {
                                    'ingredient': {
                                        'ingredient_id': 1,
                                        'name': 'Flour',
                                        'image_url': 'http://example.com/flour.jpg'
                                    },
                                    'quantity': 2.5,
                                    'unit': 'cups'
                                }
                            ],
                            'categories': [
                                {
                                    'category_id': 1,
                                    'name': 'Italian',
                                    'description': 'Italian cuisine'
                                }
                            ]
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
        Handle GET requests to retrieve all recipes.
        :return: A JSON response containing a list of serialized recipe objects
                 with HTTP status code 200.
        """
        return self.handle_get_all(get_all_recipes)

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Create a new recipe',
        'parameters': [
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'food_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the associated food item'
                        },
                        'instruction': {
                            'type': 'string',
                            'example': 'Mix ingredients and bake',
                            'description': 'Cooking instructions'
                        },
                        'prep_time': {
                            'type': 'integer',
                            'example': 30,
                            'description': 'Preparation time in minutes'
                        },
                        'cook_time': {
                            'type': 'integer',
                            'example': 45,
                            'description': 'Cooking time in minutes'
                        },
                        'servings': {
                            'type': 'integer',
                            'example': 4,
                            'description': 'Number of servings'
                        }
                    },
                    'required': ['food_id', 'instruction', 'prep_time', 'cook_time', 'servings']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'The created recipe',
                'examples': {
                    'application/json': {
                        'recipe_id': 2,
                        'food_id': 2,
                        'instruction': 'Grill the patty',
                        'prep_time': 10,
                        'cook_time': 15,
                        'servings': 2
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
        Handle POST requests to create a new recipe.
        :return: A JSON response with the serialized new recipe object on success,
                 or an error message if recipe creation fails.
        """
        return self.handle_create(create_recipe, request.json)


@class_cache
class RecipeResource(Resource, ResourceMixin):
    """
    Resource for handling operations on a single recipe identified by its recipe_id.
    Supports GET for retrieving, PUT for updating, and DELETE for deleting a recipe.
    """

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Get a specific recipe by ID',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe to retrieve'
            }
        ],
        'responses': {
            200: {
                'description': 'The requested recipe with full details',
                'examples': {
                    'application/json': {
                        'recipe_id': 1,
                        'food_id': 1,
                        'instruction': 'Mix ingredients and bake',
                        'prep_time': 30,
                        'cook_time': 45,
                        'servings': 4,
                        'food': {
                            'food_id': 1,
                            'name': 'Pizza',
                            'description': 'Italian dish',
                            'image_url': 'http://example.com/pizza.jpg'
                        },
                        'nutritional_info': {
                            'nutritional_info_id': 1,
                            'recipe_id': 1,
                            'calories': 500,
                            'protein': 20.5,
                            'carbs': 60.2,
                            'fat': 15.3
                        },
                        'ingredients': [
                            {
                                'ingredient': {
                                    'ingredient_id': 1,
                                    'name': 'Flour',
                                    'image_url': 'http://example.com/flour.jpg'
                                },
                                'quantity': 2.5,
                                'unit': 'cups'
                            }
                        ],
                        'categories': [
                            {
                                'category_id': 1,
                                'name': 'Italian',
                                'description': 'Italian cuisine'
                            }
                        ]
                    }
                }
            },
            404: {
                'description': 'Recipe not found',
                'examples': {
                    'application/json': {
                        'error': 'Recipe not found'
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        return self.handle_get_by_id(get_recipe_by_id, recipe_id)

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Update an existing recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe to update'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'food_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'Updated food ID'
                        },
                        'instruction': {
                            'type': 'string',
                            'example': 'Updated instructions',
                            'description': 'Updated cooking instructions'
                        },
                        'prep_time': {
                            'type': 'integer',
                            'example': 20,
                            'description': 'Updated preparation time in minutes'
                        },
                        'cook_time': {
                            'type': 'integer',
                            'example': 40,
                            'description': 'Updated cooking time in minutes'
                        },
                        'servings': {
                            'type': 'integer',
                            'example': 6,
                            'description': 'Updated number of servings'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'The updated recipe',
                'examples': {
                    'application/json': {
                        'recipe_id': 1,
                        'food_id': 1,
                        'instruction': 'Updated instructions',
                        'prep_time': 20,
                        'cook_time': 40,
                        'servings': 6
                    }
                }
            },
            404: {
                'description': 'Recipe not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def put(self, recipe_id):
        """
        Handle PUT requests to update an existing recipe.
        :param recipe_id: The unique identifier of the recipe to update.
        :return: A JSON response with the serialized updated recipe object,
                 or an error message if the update fails.
        """
        return self.handle_update(update_recipe, recipe_id, request.get_json())

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Delete a specific recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe to delete'
            }
        ],
        'responses': {
            204: {
                'description': 'Recipe deleted successfully'
            },
            404: {
                'description': 'Recipe not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove a specific recipe by its recipe_id.
        :param recipe_id: The unique identifier of the recipe to delete.
        :return: An empty response with status code 204 (No Content) on successful deletion,
                 or an error message if deletion fails.
        """
        return self.handle_delete(delete_recipe, recipe_id)


# Recipe-Ingredient Resource
@class_cache
class RecipeIngredientResource(Resource):
    """
    Resource for managing ingredients associated with a specific recipe.
    Supports POST for adding, GET for retrieving, PUT for updating, and DELETE for
    removing an ingredient from a recipe.
    """

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Add an ingredient to a recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'ingredient_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the ingredient to add'
                        },
                        'quantity': {
                            'type': 'number',
                            'example': 2.5,
                            'description': 'Quantity of the ingredient'
                        },
                        'unit': {
                            'type': 'string',
                            'example': 'cups',
                            'description': 'Unit of measurement',
                            'default': 'piece'
                        }
                    },
                    'required': ['ingredient_id', 'quantity']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Ingredient added successfully',
                'examples': {
                    'application/json': {
                        'message': 'Ingredient added successfully!',
                        'recipe_id': 1
                    }
                }
            },
            400: {
                'description': 'Missing required fields',
                'examples': {
                    'application/json': {
                        'error': 'ingredient_id and quantity are required.'
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def post(self, recipe_id):
        """
        Handle POST requests to add an ingredient to a recipe.
        Expects JSON data with 'ingredient_id', 'quantity', and optionally 'unit'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message and status code 201 if the ingredient
                 is added, or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit", "piece")

        if not ingredient_id or not quantity:
            return Response(
                json.dumps({"error": "ingredient_id and quantity are required."}),
                400,
                mimetype="application/json"
            )

        try:
            add_ingredient_to_recipe(recipe_id, ingredient_id, quantity, unit)
            return Response(
                json.dumps({
                    "message": "Ingredient added successfully!",
                    "recipe_id": recipe_id
                }),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Get a recipe with all its ingredients',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            }
        ],
        'responses': {
            200: {
                'description': 'The requested recipe with ingredients',
                'examples': {
                    'application/json': {
                        'recipe_id': 1,
                        'food_id': 1,
                        'instruction': 'Mix ingredients and bake',
                        'prep_time': 30,
                        'cook_time': 45,
                        'servings': 4,
                        'ingredients': [
                            {
                                'ingredient': {
                                    'ingredient_id': 1,
                                    'name': 'Flour',
                                    'image_url': 'http://example.com/flour.jpg'
                                },
                                'quantity': 2.5,
                                'unit': 'cups'
                            }
                        ]
                    }
                }
            },
            404: {
                'description': 'Recipe not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe (including its ingredients).
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            return Response(
                json.dumps(recipe.serialize()),
                200,
                mimetype="application/json"
            )
        return Response(
            json.dumps({"error": "Recipe not found"}),
            404,
            mimetype="application/json"
        )

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Update an ingredient in a recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'ingredient_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the ingredient to update'
                        },
                        'quantity': {
                            'type': 'number',
                            'example': 3.0,
                            'description': 'Updated quantity'
                        },
                        'unit': {
                            'type': 'string',
                            'example': 'tablespoons',
                            'description': 'Updated unit of measurement'
                        }
                    },
                    'required': ['ingredient_id']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Ingredient updated successfully',
                'examples': {
                    'application/json': {
                        'message': 'Ingredient updated successfully!',
                        'recipe_id': 1
                    }
                }
            },
            400: {
                'description': 'Missing required fields'
            },
            404: {
                'description': 'Recipe or ingredient not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def put(self, recipe_id):
        """
        Handle PUT requests to update an ingredient's details within a recipe.
        Expects JSON data with 'ingredient_id', and optionally 'quantity' and 'unit'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the ingredient is updated,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")
        quantity = data.get("quantity")
        unit = data.get("unit")

        if not ingredient_id:
            return Response(
                json.dumps({"error": "ingredient_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            update_recipe_ingredient(recipe_id, ingredient_id, quantity, unit)
            return Response(
                json.dumps({
                    "message": "Ingredient updated successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Remove an ingredient from a recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'ingredient_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the ingredient to remove'
                        }
                    },
                    'required': ['ingredient_id']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Ingredient removed successfully',
                'examples': {
                    'application/json': {
                        'message': 'Ingredient removed successfully!',
                        'recipe_id': 1
                    }
                }
            },
            400: {
                'description': 'Missing required fields'
            },
            404: {
                'description': 'Recipe or ingredient not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove an ingredient from a recipe.
        Expects JSON data with 'ingredient_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the ingredient is removed,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        ingredient_id = data.get("ingredient_id")

        if not ingredient_id:
            return Response(
                json.dumps({"error": "ingredient_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            remove_ingredient_from_recipe(recipe_id, ingredient_id)
            return Response(
                json.dumps({
                    "message": "Ingredient removed successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)


# Recipe-Category Resource
@class_cache
class RecipeCategoryResource(Resource):
    """
    Resource for managing categories associated with a specific recipe.
    Supports POST for adding a category to a recipe, GET for retrieving a recipe with
    categories, and DELETE for removing a category from a recipe.
    """

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Add a category to a recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'category_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the category to add'
                        }
                    },
                    'required': ['category_id']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'Category added successfully',
                'examples': {
                    'application/json': {
                        'message': 'Category added successfully!',
                        'recipe_id': 1
                    }
                }
            },
            400: {
                'description': 'Missing required fields'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def post(self, recipe_id):
        """
        Handle POST requests to add a category to a recipe.
        Expects JSON data with 'category_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the category is added,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        category_id = data.get("category_id")

        if not category_id:
            return Response(
                json.dumps({"error": "category_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            add_category_to_recipe(recipe_id, category_id)
            return Response(
                json.dumps({
                    "message": "Category added successfully!",
                    "recipe_id": recipe_id
                }),
                201,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Get a recipe with all its categories',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            }
        ],
        'responses': {
            200: {
                'description': 'The requested recipe with categories',
                'examples': {
                    'application/json': {
                        'recipe_id': 1,
                        'food_id': 1,
                        'instruction': 'Mix ingredients and bake',
                        'prep_time': 30,
                        'cook_time': 45,
                        'servings': 4,
                        'categories': [
                            {
                                'category_id': 1,
                                'name': 'Italian',
                                'description': 'Italian cuisine'
                            }
                        ]
                    }
                }
            },
            404: {
                'description': 'Recipe not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def get(self, recipe_id):
        """
        Handle GET requests to retrieve a specific recipe (including its categories).
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with the serialized recipe object if found,
                 or an error message with status code 404 if not found.
        """
        recipe = get_recipe_by_id(recipe_id)
        if recipe:
            return Response(
                json.dumps(recipe.serialize()),
                200,
                mimetype="application/json"
            )
        return Response(
            json.dumps({"error": "Recipe not found"}),
            404,
            mimetype="application/json"
        )

    @swag_from({
        'tags': ['Recipe'],
        'description': 'Remove a category from a recipe',
        'parameters': [
            {
                'name': 'recipe_id',
                'in': 'path',
                'type': 'integer',
                'required': True,
                'description': 'ID of the recipe'
            },
            {
                'in': 'body',
                'name': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'category_id': {
                            'type': 'integer',
                            'example': 1,
                            'description': 'ID of the category to remove'
                        }
                    },
                    'required': ['category_id']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Category removed successfully',
                'examples': {
                    'application/json': {
                        'message': 'Category removed successfully!',
                        'recipe_id': 1
                    }
                }
            },
            400: {
                'description': 'Missing required fields'
            },
            404: {
                'description': 'Recipe or category not found'
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def delete(self, recipe_id):
        """
        Handle DELETE requests to remove a category from a recipe.
        Expects JSON data with 'category_id'.
        :param recipe_id: The unique identifier of the recipe.
        :return: A JSON response with a success message if the category is removed,
                 or an error message if required data is missing or an error occurs.
        """
        data = request.get_json()
        category_id = data.get("category_id")

        if not category_id:
            return Response(
                json.dumps({"error": "category_id is required."}),
                400,
                mimetype="application/json"
            )

        try:
            remove_category_from_recipe(recipe_id, category_id)
            return Response(
                json.dumps({
                    "message": "Category removed successfully!",
                    "recipe_id": recipe_id
                }),
                200,
                mimetype="application/json"
            )
        except Exception as e:
            return internal_server_error(e)