from werkzeug.routing import BaseConverter

class CategoryConverter(BaseConverter):
    def __init__(self, map=None):
        super().__init__(map)

    def to_python(self, value):
        # Convert category_id to an integer for querying
        return int(value)

    def to_url(self, value):
        # Convert the Category object back to category_id for URL
        return str(value.category_id)