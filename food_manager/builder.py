"""this provides builder helper functions for hypermedia controls and
    error messages. It is used to create Mason objects that are returned as
    responses to the client.
"""
from flask import url_for

from food_manager.constants import NAMESPACE
from food_manager.models import Food, Recipe, Category, NutritionalInfo, Ingredient


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object, but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application-specific implementation details.
    """

    def add_error(self, title: str, details: str) -> None:
        """
        Adds an error element to the object. Should only be used for the root
        object and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However, we are being lazy and supporting just one
        message.

        :param title: Short title for the error
        :param details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns: str, uri: str) -> None:
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        :param ns: The namespace prefix
        :param uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {"name": uri}

    def add_control(self, ctrl_name: str, href: str, **kwargs) -> None:
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically, only certain
        properties are allowed for kwargs, but again, we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        :param ctrl_name: Name of the control (including namespace if any)
        :param href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

    # https://github.com/lorenzo-medici/PWP_StudentManager/blob/main/studentmanager/builder.py#L150
    def add_control_post(self, ctrl_name, title, href, schema):
        """
        Utility method for adding POST type controls. The control is
        constructed from the method's parameters. Method and encoding are
        fixed to "POST" and "json" respectively.

        :param str ctrl_name: Name of the control (including namespace if any)
        :param str href: target URI for the control
        :param str title: human-readable title for the control
        :param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            f"{NAMESPACE}:{ctrl_name}",
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema,
        )

    def add_control_put(self, title, href, schema):
        """
        Utility method for adding PUT type controls. The control is
        constructed from the method's parameters. Control name, method and
        encoding are fixed to "edit", "PUT" and "json" respectively.

        :param str href: Target URI for the control
        :param str title: human-readable title for the control
        :param dict schema: a dictionary representing a valid JSON schema
        """

        self.add_control(
            "edit", href, method="PUT", encoding="json", title=title, schema=schema
        )

    def add_control_delete(self, title, href):
        """
        Utility method for adding DELETE type controls. The control is
        constructed from the method's parameters. Control method is fixed to
        "DELETE", and control's name is read from the class attribute
        *DELETE_RELATION* which needs to be overridden by the child class.

        :param str href: Target URI for the control
        :param str title: human-readable title for the control
        """

        self.add_control(
            f"{NAMESPACE}:delete",
            href,
            method="DELETE",
            title=title,
        )


class FoodManagerBuilder(MasonBuilder):
    """
    A subclass of MasonBuilder that provides methods for adding application-specific
    elements to the Mason object. This class is specific
    to the FoodManager application.
    """

    def add_control_all_foods(self) -> None:
        """
        Adds a control to the Mason object that links to the collection of all
        foods in the database.
        """
        self.add_control(
            f"{NAMESPACE}:foods-all",
            url_for("api.foodlistresource"),
            method="GET",
            title="All foods",
        )

    def add_control_food(self, food) -> None:
        """
        Adds a control to the Mason object that links to the collection of all
        foods in the database.
        """
        self.add_control(
            f"{NAMESPACE}:food",
            url_for("api.foodresource", food_id=food),
            method="GET",
            title="Food of this recipe",
        )

    def add_control_add_food(self):
        self.add_control_post(
            "add-food",
            "Add New Food",
            url_for("api.foodlistresource"),
            Food.get_schema()
        )

    def add_control_edit_food(self, food):
        self.add_control_put(
            "Edit Food",
            url_for("api.foodresource", food_id=food),
            Food.get_schema()
        )

    def add_control_delete_food(self, food):
        self.add_control_delete(
            "Delete Food",
            url_for("api.foodresource", food_id=food)
        )

    def add_control_all_recipes(self) -> None:
        """
        Adds a control to the Mason object that links to the collection of all
        recipes in the database.
        """
        self.add_control(
            f"{NAMESPACE}:recipes-all",
            url_for("api.recipelistresource"),
            method="GET",
            title="All recipes",
        )

    def add_control_add_recipe(self, food_id=None):
        self.add_control_post(
            "add-recipe",
            "Add New Recipe",
            url_for("api.recipelistresource"),
            Recipe.get_schema(default_food_id=food_id)
        )

    def add_control_edit_recipe(self, recipe, food_id=None):
        self.add_control_put(
            "Edit Recipe",
            url_for("api.reciperesource", recipe_id=recipe),
            Recipe.get_schema(default_food_id=food_id)
        )

    def add_control_delete_recipe(self, recipe):
        self.add_control_delete(
            "Delete Recipe",
            url_for("api.reciperesource", recipe_id=recipe)
        )

    def add_control_all_categories(self) -> None:
        """
        Adds a control to the Mason object that links to the collection of all
        categories in the database.
        """
        self.add_control(
            f"{NAMESPACE}:categories-all",
            url_for("api.categorylistresource"),
            method="GET",
            title="All categories",
        )

    def add_control_add_category(self):
        self.add_control_post(
            "add-category",
            "Add New Category",
            url_for("api.categorylistresource"),
            Category.get_schema()
        )

    def add_control_edit_category(self, category):
        self.add_control_put(
            "Edit Category",
            url_for("api.categoryresource", category_id=category),
            Category.get_schema()
        )

    def add_control_delete_category(self, category):
        self.add_control_delete(
            "Delete Category",
            url_for("api.categoryresource", category_id=category)
        )

    def add_control_add_nutritional_info(self):
        self.add_control_post(
            "add-nutritional-info",
            "Add New Nutritional Info",
            url_for("api.nutritionalinfolistresource"),
            NutritionalInfo.get_schema()
        )

    def add_control_edit_nutritional_info(self, nutritional_info, recipe_id=None):
        self.add_control_put(
            "Edit Nutritional info",
            url_for("api.nutritionalinforesource", nutritional_info_id=nutritional_info),
            NutritionalInfo.get_schema(recipe_id)
        )

    def add_control_delete_nutritional_info(self, nutritional_info):
        self.add_control_delete(
            "Delete Nutritional info",
            url_for("api.nutritionalinforesource", nutritional_info_id=nutritional_info)
        )

    def add_control_all_ingredients(self) -> None:
        """
        Adds a control to the Mason object that links to the collection of all
        ingredients in the database.
        """
        self.add_control(
            f"{NAMESPACE}:ingredients-all",
            url_for("api.ingredientlistresource"),
            method="GET",
            title="All ingredients",
        )

    def add_control_add_ingredient(self):
        self.add_control_post(
            "add-ingredient",
            "Add New ingredient",
            url_for("api.ingredientlistresource"),
            Ingredient.get_schema()
        )

    def add_control_edit_ingredient(self, ingredient):
        self.add_control_put(
            "Edit Ingredient",
            url_for("api.ingredientresource", ingredient_id=ingredient),
            Ingredient.get_schema()
        )

    def add_control_delete_ingredient(self, ingredient):
        self.add_control_delete(
            "Delete Ingredient",
            url_for("api.ingredientresource", ingredient_id=ingredient)
        )
