"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""

"""
Module for Category API endpoints.

This module defines resources for handling categories, including
retrieving all categories and creating, updating, and deleting a single
category.
"""

import json
from flask_restful import Resource, request
from flasgger import swag_from
from flask import Response, url_for

from food_manager.db_operations import (
    create_category, get_category_by_id, get_all_categories, update_category,
    delete_category
)
from food_manager.utils.reponses import ResourceMixin
from food_manager.utils.cache import class_cache
from food_manager.builder import FoodManagerBuilder
from food_manager.constants import MASON, NAMESPACE, LINK_RELATIONS_URL, CATEGORY_PROFILE


@class_cache
class CategoryListResource(Resource, ResourceMixin):
    def get(self):
        categories = get_all_categories()
        body = FoodManagerBuilder(categories=[])
        body.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.categorylistresource"))
        body.add_control_profile()
        body.add_control_add_category()

        for cat in categories:
            category = FoodManagerBuilder(cat.serialize())
            category.add_control("self", url_for("api.categoryresource", category_id=cat.category_id))
            category.add_control("profile", CATEGORY_PROFILE)
            body["categories"].append(category)

        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        data = request.get_json()
        category = create_category(data)
        builder = FoodManagerBuilder(category.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.categoryresource", category_id=category.category_id))
        builder.add_control_profile()
        builder.add_control_all_categories()
        return Response(json.dumps(builder), 201, mimetype=MASON)


@class_cache
class CategoryResource(Resource, ResourceMixin):
    def get(self, category_id):
        category = get_category_by_id(category_id)
        if not category:
            builder = FoodManagerBuilder()
            builder.add_error("Category not found", f"No category with ID {category_id} exists.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(category.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        self_url = url_for("api.categoryresource", category_id=category_id)
        builder.add_control("self", self_url)
        builder.add_control("profile", CATEGORY_PROFILE)
        builder.add_control("collection", url_for("api.categorylistresource"))
        builder.add_control_put("Edit this category", self_url, {
            "name": "string",
            "description": "string"
        })
        builder.add_control_delete("Delete this category", self_url)
        return Response(json.dumps(builder), 200, mimetype=MASON)

    def put(self, category_id):
        data = request.get_json()
        updated = update_category(category_id, data)
        if not updated:
            builder = FoodManagerBuilder()
            builder.add_error("Category not found", f"No category with ID {category_id} exists to update.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        builder = FoodManagerBuilder(updated.serialize())
        builder.add_namespace(NAMESPACE, LINK_RELATIONS_URL)
        builder.add_control("self", url_for("api.categoryresource", category_id=category_id))
        builder.add_control("profile", CATEGORY_PROFILE)
        builder.add_control("collection", url_for("api.categorylistresource"))
        return Response(json.dumps(builder), 200, mimetype=MASON)

    def delete(self, category_id):
        success = delete_category(category_id)
        if not success:
            builder = FoodManagerBuilder()
            builder.add_error("Category not found", f"No category with ID {category_id} exists to delete.")
            return Response(json.dumps(builder), 404, mimetype=MASON)

        return Response(status=204)
