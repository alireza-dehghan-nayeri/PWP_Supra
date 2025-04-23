from flask import url_for

NAMESPACE = "foodmanager"
LINK_RELATIONS_URL = "/foodmanager/link-relations/"


class MasonBuilder(dict):
    def add_error(self, title: str, details: str) -> None:
        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns: str, uri: str) -> None:
        if "@namespaces" not in self:
            self["@namespaces"] = {}
        self["@namespaces"][ns] = {"name": uri}

    def add_control(self, ctrl_name: str, href: str, **kwargs) -> None:
        if "@controls" not in self:
            self["@controls"] = {}
        self["@controls"][ctrl_name] = {"href": href, **kwargs}

    def add_control_post(self, ctrl_name, title, href, schema):
        self.add_control(
            f"{NAMESPACE}:{ctrl_name}",
            href,
            method="POST",
            encoding="json",
            title=title,
            schema=schema,
        )

    def add_control_put(self, title, href, schema):
        self.add_control(
            "edit",
            href,
            method="PUT",
            encoding="json",
            title=title,
            schema=schema,
        )

    def add_control_delete(self, title, href):
        self.add_control(
            f"{NAMESPACE}:delete",
            href,
            method="DELETE",
            title=title,
        )


class FoodManagerBuilder(MasonBuilder):
    def add_control_all_categories(self) -> None:
        self.add_control(
            f"{NAMESPACE}:categories-all",
            url_for("api.categorylistresource"),
            method="GET",
            title="All categories",
        )

    def add_control_get_category(self, category_id: int) -> None:
        self.add_control(
            f"{NAMESPACE}:category",
            url_for("api.categoryresource", category_id=category_id),
            method="GET",
            title="Get category",
        )

    def add_control_profile(self) -> None:
        self.add_control("profile", LINK_RELATIONS_URL)

    def add_control_add_category(self):
        self.add_control_post(
            "add-category",
            "Add new Category",
            url_for("api.categorylistresource"),
            {
                "name": "string",
                "description": "string",
            },
        )
