"""
Food Manager Curses Client

A terminal-based interactive client for the Food Manager API using curses.
Provides full CRUD operations for all resources with a user-friendly interface.
"""

import curses
from curses import wrapper
import requests
from urllib.parse import urljoin
from requests.exceptions import RequestException
import json

BASE_URL = "http://127.0.0.1:5000/api/"
NAMESPACE = "foodmanager"
HEADERS = {"Accept": "application/vnd.mason+json"}

class FoodManagerClient:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.current_resource = None
        self.current_data = None
        self.history = []
        
        # Initialize windows
        self.init_windows()
        
    def init_windows(self):
        """Initialize the curses windows for the interface"""
        self.stdscr.clear()
        curses.curs_set(0)  # Hide cursor
        self.stdscr.addstr(0, 0, "Food Manager Client", curses.A_BOLD)
        
        # Main windows
        self.menu_win = curses.newwin(10, 40, 1, 0)
        self.content_win = curses.newwin(curses.LINES-12, curses.COLS-42, 1, 41)
        self.status_win = curses.newwin(1, curses.COLS, curses.LINES-1, 0)
        
        self.refresh_all()
    
    def refresh_all(self):
        """Refresh all windows"""
        self.stdscr.refresh()
        self.menu_win.refresh()
        self.content_win.refresh()
        self.status_win.refresh()
    
    def display_status(self, message):
        """Display a status message"""
        self.status_win.clear()
        self.status_win.addstr(0, 0, message)
        self.status_win.refresh()
    
    def clear_content(self):
        """Clear the content window"""
        self.content_win.clear()
        self.content_win.refresh()
    
    def display_data(self, data, title=None):
        """Display data in the content window"""
        self.clear_content()
        if title:
            self.content_win.addstr(0, 0, title, curses.A_BOLD)
        
        if isinstance(data, dict):
            y = 2
            for key, value in data.items():
                if key.startswith("@"):  # Skip hypermedia controls
                    continue
                if isinstance(value, (dict, list)):
                    self.content_win.addstr(y, 0, f"{key}:")
                    y += 1
                    self.display_nested(value, y, 4)
                    y += len(str(value).split("\n")) + 1
                else:
                    self.content_win.addstr(y, 0, f"{key}: {value}")
                    y += 1
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.content_win.addstr(i+2, 0, str(item))
        else:
            self.content_win.addstr(2, 0, str(data))
        
        self.content_win.refresh()
    
    def display_nested(self, data, y, indent):
        """Display nested data structures"""
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    self.content_win.addstr(y, indent, f"{k}:")
                    y += 1
                    self.display_nested(v, y, indent+4)
                    y += len(str(v).split("\n")) + 1
                else:
                    self.content_win.addstr(y, indent, f"{k}: {v}")
                    y += 1
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.display_nested(item, y, indent)
                    y += len(str(item).split("\n")) + 1
                else:
                    self.content_win.addstr(y, indent, str(item))
                    y += 1
        return y
    
    def get_input(self, prompt):
        """Get user input with a prompt"""
        self.status_win.clear()
        self.status_win.addstr(0, 0, prompt)
        self.status_win.refresh()
        
        curses.echo()
        input_str = self.status_win.getstr(0, len(prompt)+1).decode('utf-8')
        curses.noecho()
        
        self.status_win.clear()
        self.status_win.refresh()
        
        return input_str
    
    def make_request(self, method, url, data=None):
        """Make an HTTP request and handle errors"""
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            
            response.raise_for_status()
            return response.json() if response.content else None
        
        except RequestException as e:
            self.display_status(f"Error: {str(e)}")
            return None
    
    def follow_control(self, response, control_name):
        """Follow a hypermedia control"""
        if not response or "@controls" not in response:
            self.display_status("No controls available")
            return None
        
        controls = response["@controls"]
        if control_name not in controls:
            self.display_status(f"Control '{control_name}' not found")
            return None
        
        control = controls[control_name]
        method = control.get("method", "GET").upper()
        href = control["href"]
        url = urljoin(BASE_URL, href)
        
        # For POST/PUT, get input based on schema
        data = None
        if method in ["POST", "PUT"] and "schema" in control:
            data = self.get_input_from_schema(control["schema"])
            if data is None:  # User cancelled
                return None
        
        return self.make_request(method, url, data)
    
    def get_input_from_schema(self, schema):
        """Get user input based on a JSON schema"""
        data = {}
        self.clear_content()
        
        if "required" in schema:
            for field in schema["required"]:
                if field not in schema["properties"]:
                    continue
                
                prop = schema["properties"][field]
                prompt = f"Enter {field} ({prop.get('type', 'string')}): "
                value = self.get_input(prompt)
                
                if not value:
                    return None  # User cancelled
                
                # Convert to appropriate type
                if prop.get("type") == "integer":
                    try:
                        value = int(value)
                    except ValueError:
                        self.display_status(f"Invalid integer for {field}")
                        return None
                elif prop.get("type") == "number":
                    try:
                        value = float(value)
                    except ValueError:
                        self.display_status(f"Invalid number for {field}")
                        return None
                
                data[field] = value
        
        return data
    
    def main_menu(self):
        """Display the main menu and handle navigation"""
        options = [
            "Categories",
            "Foods",
            "Ingredients",
            "Recipes",
            "Nutritional Info",
            "Exit"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Main Menu", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            # Get user selection
            key = self.menu_win.getch()
            if key == ord('1'):
                self.category_menu()
            elif key == ord('2'):
                self.food_menu()
            elif key == ord('3'):
                self.ingredient_menu()
            elif key == ord('4'):
                self.recipe_menu()
            elif key == ord('5'):
                self.nutritional_info_menu()
            elif key == ord('6') or key == 27:  # 27 is ESC
                return
    
    def category_menu(self):
        """Category management menu"""
        response = self.make_request("GET", urljoin(BASE_URL, "categories/"))
        if not response:
            return
        
        self.current_resource = response
        self.display_categories(response.get("items", []), "Categories")
        
        options = [
            "View Category",
            "Add Category",
            "Edit Category",
            "Delete Category",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Category Menu", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_category()
            elif key == ord('2'):
                self.add_category()
            elif key == ord('3'):
                self.edit_category()
            elif key == ord('4'):
                self.delete_category()
            elif key == ord('5') or key == 27:
                return

    def display_categories(self, categories, title=None):
        """Display categories in a formatted way"""
        self.clear_content()
        if title:
            self.content_win.addstr(0, 0, title, curses.A_BOLD)
        
        if not categories:
            self.content_win.addstr(2, 0, "No categories found")
            self.content_win.refresh()
            return
        
        y = 2
        for category in categories:
            self.content_win.addstr(y, 0, f"{category['category_id']}. {category['name']}")
            self.content_win.addstr(y+1, 4, f"Description: {category['description']}")
            y += 3
        
        self.content_win.refresh()

    def view_category(self):
        """View a specific category"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No categories available")
            return
        
        categories = self.current_resource["items"]
        if not categories:
            self.display_status("No categories to view")
            return
        
        # Let user select a category
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Category:", curses.A_BOLD)
        
        for i, cat in enumerate(categories):
            name = cat.get("name", f"Category {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(categories)+3, 2, f"{len(categories)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(categories):  # 1-n
            selected = categories[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.display_category_details(response)
        elif key == 27:
            return
        
    def display_categories(self, categories, title=None):
        """Display categories in a formatted way with proper bounds checking"""
        self.clear_content()
        if title:
            try:
                self.content_win.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass  # Handle case where window is too small
            
        if not categories:
            try:
                self.content_win.addstr(2, 0, "No categories found")
            except curses.error:
                pass
            self.content_win.refresh()
            return
        
        max_y, max_x = self.content_win.getmaxyx()
        y = 2
        
        for category in categories:
            # Ensure we have space to display the category
            if y >= max_y - 2:  # Leave room for at least one more line
                break
                
            try:
                # Display category ID and name
                self.content_win.addstr(y, 0, f"{category['category_id']}. {category['name']}")
                
                # Display description (truncated if necessary)
                desc = f"Description: {category.get('description', 'N/A')}"
                if len(desc) > max_x - 4:  # Account for indentation
                    desc = desc[:max_x - 7] + "..."
                try:
                    self.content_win.addstr(y+1, 4, desc)
                except curses.error:
                    pass
                
                y += 3  # Move down for next category
                
            except curses.error:
                y += 1  # Move down if we couldn't display this category
                continue
        
        self.content_win.refresh()
    
    def display_category_details(self, category):
        """Display detailed view of a single category with bounds checking"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, "Category Details", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        for field in ['category_id', 'name', 'description']:
            if y >= max_y - 1:
                break
                
            value = str(category.get(field, 'N/A'))
            if len(value) > max_x - len(field) - 3:  # Account for field name and colon
                value = value[:max_x - len(field) - 6] + "..."
                
            try:
                self.content_win.addstr(y, 0, f"{field.capitalize()}: {value}")
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Show available controls if there's space
        if "@controls" in category and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in category["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile", "collection"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()  # Wait for any key press
    
    def add_category(self):
        """Add a new category"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add category - no controls available")
            return
        
        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-category" not in controls:
            self.display_status("Add control not found")
            return
        
        # Get input based on the schema
        schema = controls[f"{NAMESPACE}:add-category"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return  # User cancelled
        
        # Make the request
        control = controls[f"{NAMESPACE}:add-category"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)
        
        if response:
            self.display_status("Category added successfully")
            # Refresh the category list
            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "categories/"))
            if self.current_resource:
                self.display_categories(self.current_resource.get("items", []), "Categories")

    def edit_category(self):
        """Edit an existing category"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No categories available")
            return
        
        categories = self.current_resource["items"]
        if not categories:
            self.display_status("No categories to edit")
            return
        
        # Let user select a category
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Category to Edit:", curses.A_BOLD)
        
        for i, cat in enumerate(categories):
            name = cat.get("name", f"Category {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(categories)+3, 2, f"{len(categories)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(categories):  # 1-n
            selected = categories[key-49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                # Get current values for pre-filling the form
                current_values = {
                    "name": selected.get("name", ""),
                    "description": selected.get("description", "")
                }
                
                # Get updated values from user
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return  # User cancelled
                
                # Make the request
                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)
                
                if response:
                    self.display_status("Category updated successfully")
                    # Refresh the category list
                    self.current_resource = self.make_request("GET", urljoin(BASE_URL, "categories/"))
                    if self.current_resource:
                        self.display_categories(self.current_resource.get("items", []), "Categories")
        elif key == 27:
            return

    def delete_category(self):
        """Delete a category"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No categories available")
            return
        
        categories = self.current_resource["items"]
        if not categories:
            self.display_status("No categories to delete")
            return
        
        # Let user select a category
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Category to Delete:", curses.A_BOLD)
        
        for i, cat in enumerate(categories):
            name = cat.get("name", f"Category {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(categories)+3, 2, f"{len(categories)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(categories):  # 1-n
            selected = categories[key-49]
            if "@controls" in selected and f"{NAMESPACE}:delete" in selected["@controls"]:
                # Confirm deletion
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()
                
                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"][f"{NAMESPACE}:delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Category deleted successfully")
                        # Refresh the category list
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "categories/"))
                        if self.current_resource:
                            self.display_categories(self.current_resource.get("items", []), "Categories")
        elif key == 27:
            return

    def get_input_from_schema(self, schema, initial_values=None):
        """Get user input based on a JSON schema with optional initial values"""
        data = {}
        self.clear_content()
        
        if not schema or "properties" not in schema:
            return None
        
        initial_values = initial_values or {}
        required_fields = schema.get("required", [])
        properties = schema["properties"]
        
        y = 0
        for field, config in properties.items():
            prompt = f"Enter {field} ({config.get('type', 'string')}): "
            default_value = str(initial_values.get(field, ""))
            
            self.content_win.addstr(y, 0, prompt)
            self.content_win.addstr(y, len(prompt), default_value)
            self.content_win.refresh()
            
            curses.echo()
            input_str = self.content_win.getstr(y, len(prompt), 50).decode('utf-8')
            curses.noecho()
            
            if not input_str and field in required_fields:
                self.display_status(f"{field} is required!")
                return None
            
            # Convert to appropriate type
            if config.get("type") == "integer":
                try:
                    data[field] = int(input_str) if input_str else None
                except ValueError:
                    self.display_status(f"Invalid integer for {field}")
                    return None
            elif config.get("type") == "number":
                try:
                    data[field] = float(input_str) if input_str else None
                except ValueError:
                    self.display_status(f"Invalid number for {field}")
                    return None
            else:
                data[field] = input_str if input_str else None
            
            y += 2
        
        return data
    
    def food_menu(self):
        """Food management menu"""
        response = self.make_request("GET", urljoin(BASE_URL, "foods/"))
        if not response:
            return
        
        self.current_resource = response
        self.display_foods(response.get("items", []), "Food Items")
        
        options = [
            "View Food Details",
            "Add Food",
            "Edit Food",
            "Delete Food",
            "Manage Recipes",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Food Menu", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_food()
            elif key == ord('2'):
                self.add_food()
            elif key == ord('3'):
                self.edit_food()
            elif key == ord('4'):
                self.delete_food()
            elif key == ord('5'):
                self.manage_food_recipes()
            elif key == ord('6') or key == 27:
                return

    def display_foods(self, foods, title=None):
        """Display food items in a formatted way"""
        self.clear_content()
        if title:
            try:
                self.content_win.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass
        
        if not foods:
            try:
                self.content_win.addstr(2, 0, "No food items found")
            except curses.error:
                pass
            self.content_win.refresh()
            return
        
        max_y, max_x = self.content_win.getmaxyx()
        y = 2
        
        for food in foods:
            if y >= max_y - 3:  # Leave room for at least one more item
                break
                
            try:
                # Display basic food info
                self.content_win.addstr(y, 0, f"{food['food_id']}. {food['name']}")
                
                # Display description (truncated if needed)
                desc = food.get('description', 'No description')
                if len(desc) > max_x - 4:
                    desc = desc[:max_x - 7] + "..."
                try:
                    self.content_win.addstr(y+1, 4, desc)
                except curses.error:
                    pass
                
                # Display recipe count
                recipe_count = len(food.get('recipes', []))
                try:
                    self.content_win.addstr(y+2, 4, f"Recipes: {recipe_count}")
                except curses.error:
                    pass
                
                y += 4  # Space between items
                
            except curses.error:
                y += 1
                continue
        
        self.content_win.refresh()

    def view_food(self):
        """View detailed information about a specific food item"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No food items available")
            return
        
        foods = self.current_resource["items"]
        if not foods:
            self.display_status("No food items to view")
            return
        
        # Let user select a food item
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Food Item:", curses.A_BOLD)
        
        for i, food in enumerate(foods):
            name = food.get("name", f"Food {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(foods)+3, 2, f"{len(foods)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(foods):  # 1-n
            selected = foods[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.display_food_details(response)
        elif key == 27:
            return

    def display_food_details(self, food):
        """Display detailed information about a food item"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, "Food Details", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        details = [
            f"ID: {food.get('food_id', 'N/A')}",
            f"Name: {food.get('name', 'N/A')}",
            f"Description: {food.get('description', 'N/A')}",
            f"Image URL: {food.get('image_url', 'None')}"
        ]
        
        for detail in details:
            if y >= max_y - 1:
                break
            try:
                if len(detail) > max_x:
                    detail = detail[:max_x-3] + "..."
                self.content_win.addstr(y, 0, detail)
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Display recipes if available
        if 'recipes' in food and food['recipes'] and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Recipes:", curses.A_BOLD)
                y += 1
                
                for recipe in food['recipes']:
                    if y >= max_y - 1:
                        break
                        
                    recipe_line = f"- {recipe.get('recipe_id', '?')}: {recipe.get('instruction', 'No instructions')}"
                    if len(recipe_line) > max_x:
                        recipe_line = recipe_line[:max_x-3] + "..."
                    
                    try:
                        self.content_win.addstr(y, 2, recipe_line)
                        y += 1
                    except curses.error:
                        y += 1
                        continue
            except curses.error:
                pass
        
        # Show available controls
        if "@controls" in food and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in food["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile", "collection"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()  # Wait for any key press

    def add_food(self):
        """Add a new food item"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add food - no controls available")
            return
        
        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-food" not in controls:
            self.display_status("Add control not found")
            return
        
        # Get input based on the schema
        schema = controls[f"{NAMESPACE}:add-food"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return  # User cancelled
        
        # Make the request
        control = controls[f"{NAMESPACE}:add-food"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)
        
        if response:
            self.display_status("Food added successfully")
            # Refresh the food list
            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "foods/"))
            if self.current_resource:
                self.display_foods(self.current_resource.get("items", []), "Food Items")

    def edit_food(self):
        """Edit an existing food item"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No food items available")
            return
        
        foods = self.current_resource["items"]
        if not foods:
            self.display_status("No food items to edit")
            return
        
        # Let user select a food item
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Food to Edit:", curses.A_BOLD)
        
        for i, food in enumerate(foods):
            name = food.get("name", f"Food {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(foods)+3, 2, f"{len(foods)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(foods):  # 1-n
            selected = foods[key-49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                # Get current values for pre-filling the form
                current_values = {
                    "name": selected.get("name", ""),
                    "description": selected.get("description", ""),
                    "image_url": selected.get("image_url", "")
                }
                
                # Get updated values from user
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return  # User cancelled
                
                # Make the request
                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)
                
                if response:
                    self.display_status("Food updated successfully")
                    # Refresh the food list
                    self.current_resource = self.make_request("GET", urljoin(BASE_URL, "foods/"))
                    if self.current_resource:
                        self.display_foods(self.current_resource.get("items", []), "Food Items")
        elif key == 27:
            return

    def delete_food(self):
        """Delete a food item"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No food items available")
            return
        
        foods = self.current_resource["items"]
        if not foods:
            self.display_status("No food items to delete")
            return
        
        # Let user select a food item
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Food to Delete:", curses.A_BOLD)
        
        for i, food in enumerate(foods):
            name = food.get("name", f"Food {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(foods)+3, 2, f"{len(foods)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(foods):  # 1-n
            selected = foods[key-49]
            if "@controls" in selected and f"{NAMESPACE}:delete" in selected["@controls"]:
                # Confirm deletion
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()
                
                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"][f"{NAMESPACE}:delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Food deleted successfully")
                        # Refresh the food list
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "foods/"))
                        if self.current_resource:
                            self.display_foods(self.current_resource.get("items", []), "Food Items")
        elif key == 27:
            return

    def manage_food_recipes(self):
        """Manage recipes for a specific food item"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No food items available")
            return
        
        foods = self.current_resource["items"]
        if not foods:
            self.display_status("No food items to manage recipes for")
            return
        
        # Let user select a food item
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Food Item:", curses.A_BOLD)
        
        for i, food in enumerate(foods):
            name = food.get("name", f"Food {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(foods)+3, 2, f"{len(foods)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(foods):  # 1-n
            selected = foods[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.recipe_management_menu(response)
        elif key == 27:
            return

    def recipe_management_menu(self, food_response):
        """Menu for managing recipes for a specific food item"""
        self.current_resource = food_response
        self.display_food_recipes(food_response)
        
        options = [
            "View Recipe",
            "Add Recipe",
            "Edit Recipe",
            "Delete Recipe",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, f"Recipes for {food_response.get('name', 'Food')}", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_recipe()
            elif key == ord('2'):
                self.add_recipe_to_food()
            elif key == ord('3'):
                self.edit_recipe()
            elif key == ord('4'):
                self.delete_recipe()
            elif key == ord('5') or key == 27:
                return

    def display_food_recipes(self, food):
        """Display recipes for a specific food item"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, f"Recipes for {food.get('name', 'Food')}", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        recipes = food.get('recipes', [])
        
        if not recipes:
            try:
                self.content_win.addstr(y, 0, "No recipes available")
                y += 1
            except curses.error:
                pass
        else:
            for recipe in recipes:
                if y >= max_y - 1:
                    break
                    
                try:
                    self.content_win.addstr(y, 0, f"Recipe {recipe.get('recipe_id', '?')}")
                    y += 1
                    
                    # Display instruction (truncated if needed)
                    instruction = recipe.get('instruction', 'No instructions')
                    if len(instruction) > max_x:
                        instruction = instruction[:max_x-3] + "..."
                    try:
                        self.content_win.addstr(y, 4, instruction)
                        y += 1
                    except curses.error:
                        y += 1
                    
                    # Display cooking info
                    cook_info = f"Prep: {recipe.get('prep_time', '?')} min | Cook: {recipe.get('cook_time', '?')} min | Serves: {recipe.get('servings', '?')}"
                    try:
                        self.content_win.addstr(y, 4, cook_info)
                        y += 2  # Extra space between recipes
                    except curses.error:
                        y += 1
                except curses.error:
                    y += 1
        
        self.content_win.refresh()

    def add_recipe_to_food(self):
        """Add a new recipe to a food item"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add recipe - no controls available")
            return
        
        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-recipe" not in controls:
            self.display_status("Add recipe control not found")
            return
        
        # Get input based on the schema
        schema = controls[f"{NAMESPACE}:add-recipe"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return  # User cancelled
        
        # Make the request
        control = controls[f"{NAMESPACE}:add-recipe"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)
        
        if response:
            self.display_status("Recipe added successfully")
            # Refresh the food details
            if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                url = self.current_resource["@controls"]["self"]["href"]
                self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                if self.current_resource:
                    self.display_food_recipes(self.current_resource)

    def view_recipe(self):
        """View detailed information about a specific recipe"""
        if not self.current_resource or "recipes" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["recipes"]
        if not recipes:
            self.display_status("No recipes to view")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            self.menu_win.addstr(i+2, 2, f"{i+1}. Recipe {recipe.get('recipe_id', '?')}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.display_recipe_details(response)
        elif key == 27:
            return

    def display_recipe_details(self, recipe):
        """Display detailed information about a recipe"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, "Recipe Details", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        details = [
            f"ID: {recipe.get('recipe_id', 'N/A')}",
            f"Food: {recipe.get('food', 'N/A')}",
            f"Prep Time: {recipe.get('prep_time', 'N/A')} minutes",
            f"Cook Time: {recipe.get('cook_time', 'N/A')} minutes",
            f"Servings: {recipe.get('servings', 'N/A')}"
        ]
        
        for detail in details:
            if y >= max_y - 1:
                break
            try:
                if len(detail) > max_x:
                    detail = detail[:max_x-3] + "..."
                self.content_win.addstr(y, 0, detail)
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Display instructions
        if 'instruction' in recipe and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Instructions:", curses.A_BOLD)
                y += 1
                
                instructions = recipe['instruction'].split('\n')
                for line in instructions:
                    if y >= max_y - 1:
                        break
                        
                    if len(line) > max_x:
                        line = line[:max_x-3] + "..."
                    
                    try:
                        self.content_win.addstr(y, 2, line)
                        y += 1
                    except curses.error:
                        y += 1
                        continue
            except curses.error:
                pass
        
        # Show available controls
        if "@controls" in recipe and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in recipe["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()  # Wait for any key press

    def edit_recipe(self):
        """Edit an existing recipe"""
        if not self.current_resource or "recipes" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["recipes"]
        if not recipes:
            self.display_status("No recipes to edit")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe to Edit:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            self.menu_win.addstr(i+2, 2, f"{i+1}. Recipe {recipe.get('recipe_id', '?')}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                # Get current values for pre-filling the form
                current_values = {
                    "instruction": selected.get("instruction", ""),
                    "prep_time": selected.get("prep_time", ""),
                    "cook_time": selected.get("cook_time", ""),
                    "servings": selected.get("servings", ""),
                    "food_id": selected.get("food_id", "")
                }
                
                # Get updated values from user
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return  # User cancelled
                
                # Make the request
                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)
                
                if response:
                    self.display_status("Recipe updated successfully")
                    # Refresh the food details
                    if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                        url = self.current_resource["@controls"]["self"]["href"]
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                        if self.current_resource:
                            self.display_food_recipes(self.current_resource)
        elif key == 27:
            return

    def delete_recipe(self):
        """Delete a recipe"""
        if not self.current_resource or "recipes" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["recipes"]
        if not recipes:
            self.display_status("No recipes to delete")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe to Delete:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            self.menu_win.addstr(i+2, 2, f"{i+1}. Recipe {recipe.get('recipe_id', '?')}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "delete" in selected["@controls"]:
                # Confirm deletion
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()
                
                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"]["delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Recipe deleted successfully")
                        # Refresh the food details
                        if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                            url = self.current_resource["@controls"]["self"]["href"]
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                            if self.current_resource:
                                self.display_food_recipes(self.current_resource)
        elif key == 27:
            return
        
    # Similar methods for Ingredients, Recipes, and Nutritional Info would follow
    # The structure would be very similar to the Category and Food methods
    
    def ingredient_menu(self):
        """Ingredient management menu"""
        response = self.make_request("GET", urljoin(BASE_URL, "ingredients/"))
        if not response:
            return
        
        self.current_resource = response
        self.display_ingredients(response.get("items", []), "Ingredients")
        
        options = [
            "View Ingredient",
            "Add Ingredient",
            "Edit Ingredient",
            "Delete Ingredient",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Ingredient Menu", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_ingredient()
            elif key == ord('2'):
                self.add_ingredient()
            elif key == ord('3'):
                self.edit_ingredient()
            elif key == ord('4'):
                self.delete_ingredient()
            elif key == ord('5') or key == 27:
                return

    def display_ingredients(self, ingredients, title=None):
        """Display ingredients in a formatted way"""
        self.clear_content()
        if title:
            try:
                self.content_win.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass
        
        if not ingredients:
            try:
                self.content_win.addstr(2, 0, "No ingredients found")
            except curses.error:
                pass
            self.content_win.refresh()
            return
        
        max_y, max_x = self.content_win.getmaxyx()
        y = 2
        
        for ingredient in ingredients:
            if y >= max_y - 2:  # Leave room for at least one more line
                break
                
            try:
                # Display ingredient ID and name
                self.content_win.addstr(y, 0, f"{ingredient['ingredient_id']}. {ingredient['name']}")
                
                # Display image URL if available
                if 'image_url' in ingredient:
                    img = f"Image: {ingredient['image_url']}"
                    if len(img) > max_x - 4:
                        img = img[:max_x - 7] + "..."
                    try:
                        self.content_win.addstr(y+1, 4, img)
                    except curses.error:
                        pass
                    y += 2
                else:
                    y += 1
                    
            except curses.error:
                y += 1
                continue
        
        self.content_win.refresh()

    def view_ingredient(self):
        """View a specific ingredient"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No ingredients available")
            return

        ingredients = self.current_resource["items"]
        if not ingredients:
            self.display_status("No ingredients to view")
            return

        # Let user select an ingredient
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, ingredient in enumerate(ingredients):
            if i + 2 < max_y:
                name = ingredient.get("name", f"Ingredient {i}")
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. {name}")

        back_line = len(ingredients) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(ingredients) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key - 49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.display_ingredient_details(response)
        elif key == 27:
            return
        
    def display_ingredient_details(self, ingredient):
        """Display detailed view of a single ingredient"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, "Ingredient Details", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        for field in ['ingredient_id', 'name', 'image_url']:
            if y >= max_y - 1:
                break
                
            value = str(ingredient.get(field, 'N/A'))
            if len(value) > max_x - len(field) - 3:
                value = value[:max_x - len(field) - 6] + "..."
                
            try:
                self.content_win.addstr(y, 0, f"{field.capitalize()}: {value}")
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Show available controls if there's space
        if "@controls" in ingredient and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in ingredient["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile", "collection"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()  # Wait for any key press

    def add_ingredient(self):
        """Add a new ingredient"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add ingredient - no controls available")
            return
        
        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-ingredient" not in controls:
            self.display_status("Add control not found")
            return
        
        # Get input based on the schema
        schema = controls[f"{NAMESPACE}:add-ingredient"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return  # User cancelled
        
        # Make the request
        control = controls[f"{NAMESPACE}:add-ingredient"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)
        
        if response:
            self.display_status("Ingredient added successfully")
            # Refresh the ingredient list
            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "ingredients/"))
            if self.current_resource:
                self.display_ingredients(self.current_resource.get("items", []), "Ingredients")

    def edit_ingredient(self):
        """Edit an existing ingredient"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No ingredients available")
            return

        ingredients = self.current_resource["items"]
        if not ingredients:
            self.display_status("No ingredients to edit")
            return

        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient to Edit:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, ingredient in enumerate(ingredients):
            if i + 2 < max_y:
                name = ingredient.get("name", f"Ingredient {i}")
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. {name}")

        back_line = len(ingredients) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(ingredients) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key - 49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                current_values = {
                    "name": selected.get("name", ""),
                    "image_url": selected.get("image_url", "")
                }
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return
                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)
                if response:
                    self.display_status("Ingredient updated successfully")
                    self.current_resource = self.make_request("GET", urljoin(BASE_URL, "ingredients/"))
                    if self.current_resource:
                        self.display_ingredients(self.current_resource.get("items", []), "Ingredients")
        elif key == 27:
            return
    
    def delete_ingredient(self):
        """Delete an ingredient"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No ingredients available")
            return

        ingredients = self.current_resource["items"]
        if not ingredients:
            self.display_status("No ingredients to delete")
            return

        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient to Delete:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, ingredient in enumerate(ingredients):
            if i + 2 < max_y:
                name = ingredient.get("name", f"Ingredient {i}")
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. {name}")

        back_line = len(ingredients) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(ingredients) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key - 49]
            if "@controls" in selected and f"{NAMESPACE}:delete" in selected["@controls"]:
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()

                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"][f"{NAMESPACE}:delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    if response is not None:
                        self.display_status("Ingredient deleted successfully")
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "ingredients/"))
                        if self.current_resource:
                            self.display_ingredients(self.current_resource.get("items", []), "Ingredients")
        elif key == 27:
            return
        
    def recipe_menu(self):
        """Recipe management menu"""
        response = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
        if not response:
            return
        
        self.current_resource = response
        self.display_recipes(response.get("items", []), "Recipes")
        
        options = [
            "View Recipe Details",
            "Add Recipe",
            "Edit Recipe",
            "Delete Recipe",
            "View Nutritional Info",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Recipe Menu", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_recipe_details()
            elif key == ord('2'):
                self.add_recipe()
            elif key == ord('3'):
                self.edit_recipe()
            elif key == ord('4'):
                self.delete_recipe()
            # elif key == ord('5'):
            #     self.manage_recipe_ingredients()
            # elif key == ord('6'):
            #     self.manage_recipe_categories()
            elif key == ord('5'):
                self.view_recipe_nutrition()
            elif key == ord('6') or key == 27:
                return

    def display_recipes(self, recipes, title=None):
        """Display recipes in a formatted way"""
        self.clear_content()
        if title:
            try:
                self.content_win.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass
        
        if not recipes:
            try:
                self.content_win.addstr(2, 0, "No recipes found")
            except curses.error:
                pass
            self.content_win.refresh()
            return
        
        max_y, max_x = self.content_win.getmaxyx()
        y = 2
        
        for recipe in recipes:
            if y >= max_y - 4:  # Leave room for at least one more item
                break
                
            try:
                # Display basic recipe info
                self.content_win.addstr(y, 0, f"{recipe['recipe_id']}. {recipe['food']}")
                
                # Display cooking times
                try:
                    self.content_win.addstr(y+1, 4, 
                        f"Prep: {recipe['prep_time']} min | Cook: {recipe['cook_time']} min | Serves: {recipe['servings']}")
                except curses.error:
                    pass
                
                # Display first line of instruction (truncated if needed)
                instruction = recipe.get('instruction', 'No instructions').split('\n')[0]
                if len(instruction) > max_x - 4:
                    instruction = instruction[:max_x - 7] + "..."
                try:
                    self.content_win.addstr(y+2, 4, instruction)
                except curses.error:
                    pass
                
                y += 4  # Space between items
                
            except curses.error:
                y += 1
                continue
        
        self.content_win.refresh()

    def view_recipe_details(self):
        """View detailed information about a specific recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to view")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.display_recipe_full_details(response)
        elif key == 27:
            return

    def display_recipe_full_details(self, recipe):
        """Display complete recipe details with ingredients and categories"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, f"Recipe: {recipe.get('food', 'N/A')}", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        details = [
            f"ID: {recipe.get('recipe_id', 'N/A')}",
            f"Prep Time: {recipe.get('prep_time', 'N/A')} minutes",
            f"Cook Time: {recipe.get('cook_time', 'N/A')} minutes",
            f"Servings: {recipe.get('servings', 'N/A')}"
        ]
        
        # Display basic details
        for detail in details:
            if y >= max_y - 1:
                break
            try:
                if len(detail) > max_x:
                    detail = detail[:max_x-3] + "..."
                self.content_win.addstr(y, 0, detail)
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Display instructions
        if 'instruction' in recipe and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Instructions:", curses.A_BOLD)
                y += 1
                
                instructions = recipe['instruction'].split('\n')
                for line in instructions:
                    if y >= max_y - 1:
                        break
                        
                    if len(line) > max_x:
                        line = line[:max_x-3] + "..."
                    
                    try:
                        self.content_win.addstr(y, 2, line)
                        y += 1
                    except curses.error:
                        y += 1
                        continue
            except curses.error:
                pass
        
        # Display ingredients if available
        if 'ingredients' in recipe and recipe['ingredients'] and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Ingredients:", curses.A_BOLD)
                y += 1
                
                for ingredient in recipe['ingredients']:
                    if y >= max_y - 1:
                        break
                    
                    ing = ingredient.get('ingredient', {})
                    line = f"- {ing.get('name', '?')}: {ingredient.get('quantity', '?')} {ingredient.get('unit', '')}"
                    if len(line) > max_x:
                        line = line[:max_x-3] + "..."
                    
                    try:
                        self.content_win.addstr(y, 2, line)
                        y += 1
                    except curses.error:
                        y += 1
                        continue
            except curses.error:
                pass
        
        # Display categories if available
        if 'categories' in recipe and recipe['categories'] and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Categories:", curses.A_BOLD)
                y += 1
                
                for category in recipe['categories']:
                    if y >= max_y - 1:
                        break
                    
                    line = f"- {category.get('name', '?')}: {category.get('description', '')}"
                    if len(line) > max_x:
                        line = line[:max_x-3] + "..."
                    
                    try:
                        self.content_win.addstr(y, 2, line)
                        y += 1
                    except curses.error:
                        y += 1
                        continue
            except curses.error:
                pass
        
        # Show available controls
        if "@controls" in recipe and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in recipe["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile", "collection"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()  # Wait for any key press

    def add_recipe(self):
        """Add a new recipe"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add recipe - no controls available")
            return
        
        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-recipe" not in controls:
            self.display_status("Add control not found")
            return
        
        # Get input based on the schema
        schema = controls[f"{NAMESPACE}:add-recipe"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return  # User cancelled
        
        # Make the request
        control = controls[f"{NAMESPACE}:add-recipe"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)
        
        if response:
            self.display_status("Recipe added successfully")
            # Refresh the recipe list
            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
            if self.current_resource:
                self.display_recipes(self.current_resource.get("items", []), "Recipes")

    def edit_recipe(self):
        """Edit an existing recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to edit")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe to Edit:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                # Get current values for pre-filling the form
                current_values = {
                    "food_id": selected.get("food_id", ""),
                    "instruction": selected.get("instruction", ""),
                    "prep_time": selected.get("prep_time", ""),
                    "cook_time": selected.get("cook_time", ""),
                    "servings": selected.get("servings", "")
                }
                
                # Get updated values from user
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return  # User cancelled
                
                # Make the request
                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)
                
                if response:
                    self.display_status("Recipe updated successfully")
                    # Refresh the recipe list
                    self.current_resource = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
                    if self.current_resource:
                        self.display_recipes(self.current_resource.get("items", []), "Recipes")
        elif key == 27:
            return

    def delete_recipe(self):
        """Delete a recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to delete")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe to Delete:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and f"{NAMESPACE}:delete" in selected["@controls"]:
                # Confirm deletion
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()
                
                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"][f"{NAMESPACE}:delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Recipe deleted successfully")
                        # Refresh the recipe list
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
                        if self.current_resource:
                            self.display_recipes(self.current_resource.get("items", []), "Recipes")
        elif key == 27:
            return

    def manage_recipe_ingredients(self):
        
        """Manage ingredients for a specific recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to manage ingredients for")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.recipe_ingredients_menu(response)
        elif key == 27:
            return

    def recipe_ingredients_menu(self, recipe_response):
        """Menu for managing a recipe's ingredients"""
        self.current_resource = recipe_response
        self.display_recipe_ingredients(recipe_response)
        
        options = [
            "Add Ingredient",
            "Edit Ingredient",
            "Remove Ingredient",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, f"Ingredients for {recipe_response.get('food', 'Recipe')}", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.add_recipe_ingredient()
            elif key == ord('2'):
                self.edit_recipe_ingredient()
            elif key == ord('3'):
                self.remove_recipe_ingredient()
            elif key == ord('4') or key == 27:
                return

    def display_recipe_ingredients(self, recipe):
        """Display ingredients for a specific recipe"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, f"Ingredients for {recipe.get('food', 'Recipe')}", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        ingredients = recipe.get('ingredients', [])
        
        if not ingredients:
            try:
                self.content_win.addstr(y, 0, "No ingredients available")
                y += 1
            except curses.error:
                pass
        else:
            for ingredient in ingredients:
                if y >= max_y - 1:
                    break
                    
                ing = ingredient.get('ingredient', {})
                try:
                    self.content_win.addstr(y, 0, 
                        f"{ing.get('name', '?')}: {ingredient.get('quantity', '?')} {ingredient.get('unit', '')}")
                    y += 1
                except curses.error:
                    y += 1
                    continue
        
        self.content_win.refresh()

    def add_recipe_ingredient(self):
        """Add an ingredient to a recipe"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add ingredient - no controls available")
            return
        
        # First get all available ingredients
        ingredients_response = self.make_request("GET", urljoin(BASE_URL, "ingredients/"))
        if not ingredients_response or "items" not in ingredients_response:
            self.display_status("Could not fetch ingredients")
            return
        
        # Let user select an ingredient
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient:", curses.A_BOLD)
        
        ingredients = ingredients_response["items"]
        for i, ingredient in enumerate(ingredients):
            name = ingredient.get("name", f"Ingredient {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(ingredients)+3, 2, f"{len(ingredients)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key-49]
            ingredient_id = selected.get("ingredient_id")
            
            # Get quantity and unit
            try:
                quantity = self.get_input("Enter quantity:")
                if not quantity:
                    return
                
                unit = self.get_input("Enter unit (optional):")
                
                # Build the request data
                data = {
                    "ingredient_id": ingredient_id,
                    "quantity": float(quantity),
                    "unit": unit or "unit"
                }
                
                # Find the add-ingredient control
                if f"{NAMESPACE}:add-ingredient" in self.current_resource["@controls"]:
                    control = self.current_resource["@controls"][f"{NAMESPACE}:add-ingredient"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url, data)
                    
                    if response:
                        self.display_status("Ingredient added successfully")
                        # Refresh the recipe
                        if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                            url = self.current_resource["@controls"]["self"]["href"]
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                            if self.current_resource:
                                self.display_recipe_ingredients(self.current_resource)
            except ValueError:
                self.display_status("Invalid quantity - must be a number")
        elif key == 27:
            return

    def edit_recipe_ingredient(self):
        """Edit an ingredient in a recipe"""
        if not self.current_resource or "ingredients" not in self.current_resource:
            self.display_status("No ingredients available to edit")
            return
        
        ingredients = self.current_resource["ingredients"]
        if not ingredients:
            self.display_status("No ingredients to edit")
            return
        
        # Let user select an ingredient
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient to Edit:", curses.A_BOLD)
        
        for i, ingredient in enumerate(ingredients):
            name = ingredient.get('ingredient', {}).get('name', f"Ingredient {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(ingredients)+3, 2, f"{len(ingredients)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key-49]
            
            # Get new quantity and unit
            try:
                current_qty = selected.get('quantity', '')
                current_unit = selected.get('unit', '')
                
                quantity = self.get_input(f"Enter new quantity (current: {current_qty}):")
                if not quantity:
                    return
                
                unit = self.get_input(f"Enter new unit (current: {current_unit}):")
                
                # Build the request data
                data = {
                    "quantity": float(quantity),
                    "unit": unit or current_unit or "unit"
                }
                
                # Find the edit control
                if "@controls" in selected and "edit" in selected["@controls"]:
                    control = selected["@controls"]["edit"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url, data)
                    
                    if response:
                        self.display_status("Ingredient updated successfully")
                        # Refresh the recipe
                        if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                            url = self.current_resource["@controls"]["self"]["href"]
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                            if self.current_resource:
                                self.display_recipe_ingredients(self.current_resource)
            except ValueError:
                self.display_status("Invalid quantity - must be a number")
        elif key == 27:
            return

    def remove_recipe_ingredient(self):
        """Remove an ingredient from a recipe"""
        if not self.current_resource or "ingredients" not in self.current_resource:
            self.display_status("No ingredients available to remove")
            return
        
        ingredients = self.current_resource["ingredients"]
        if not ingredients:
            self.display_status("No ingredients to remove")
            return
        
        # Let user select an ingredient
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Ingredient to Remove:", curses.A_BOLD)
        
        for i, ingredient in enumerate(ingredients):
            name = ingredient.get('ingredient', {}).get('name', f"Ingredient {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(ingredients)+3, 2, f"{len(ingredients)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(ingredients):  # 1-n
            selected = ingredients[key-49]
            
            # Confirm deletion
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
            self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
            self.menu_win.refresh()
            
            confirm = self.menu_win.getch()
            if confirm == ord('y'):
                if "@controls" in selected and "delete" in selected["@controls"]:
                    control = selected["@controls"]["delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Ingredient removed successfully")
                        # Refresh the recipe
                        if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                            url = self.current_resource["@controls"]["self"]["href"]
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                            if self.current_resource:
                                self.display_recipe_ingredients(self.current_resource)
        elif key == 27:
            return

    def manage_recipe_categories(self):
        """Manage categories for a specific recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to manage categories for")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "@controls" in selected and "self" in selected["@controls"]:
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response:
                    self.recipe_categories_menu(response)
        elif key == 27:
            return

    def recipe_categories_menu(self, recipe_response):
        """Menu for managing a recipe's categories"""
        self.current_resource = recipe_response
        self.display_recipe_categories(recipe_response)
        
        options = [
            "Add Category",
            "Remove Category",
            "Back"
        ]
        
        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, f"Categories for {recipe_response.get('food', 'Recipe')}", curses.A_BOLD)
            
            for i, option in enumerate(options):
                self.menu_win.addstr(i+2, 2, f"{i+1}. {option}")
            
            self.menu_win.refresh()
            
            key = self.menu_win.getch()
            if key == ord('1'):
                self.add_recipe_category()
            elif key == ord('2'):
                self.remove_recipe_category()
            elif key == ord('3') or key == 27:
                return

    def display_recipe_categories(self, recipe):
        """Display categories for a specific recipe"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, f"Categories for {recipe.get('food', 'Recipe')}", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        categories = recipe.get('categories', [])
        
        if not categories:
            try:
                self.content_win.addstr(y, 0, "No categories assigned")
                y += 1
            except curses.error:
                pass
        else:
            for category in categories:
                if y >= max_y - 1:
                    break
                    
                try:
                    self.content_win.addstr(y, 0, 
                        f"{category.get('name', '?')}: {category.get('description', '')}")
                    y += 1
                except curses.error:
                    y += 1
                    continue
        
        self.content_win.refresh()

    def add_recipe_category(self):
        """Add a category to a recipe"""
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add category - no controls available")
            return
        
        # First get all available categories
        categories_response = self.make_request("GET", urljoin(BASE_URL, "categories/"))
        if not categories_response or "items" not in categories_response:
            self.display_status("Could not fetch categories")
            return
        
        # Let user select a category
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Category:", curses.A_BOLD)
        
        categories = categories_response["items"]
        for i, category in enumerate(categories):
            name = category.get("name", f"Category {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(categories)+3, 2, f"{len(categories)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(categories):  # 1-n
            selected = categories[key-49]
            category_id = selected.get("category_id")
            
            # Find the add-category control
            if f"{NAMESPACE}:add-category" in self.current_resource["@controls"]:
                control = self.current_resource["@controls"][f"{NAMESPACE}:add-category"]
                url = urljoin(BASE_URL, control["href"])
                data = {"category_id": category_id}
                response = self.make_request(control["method"], url, data)
                
                if response:
                    self.display_status("Category added successfully")
                    # Refresh the recipe
                    if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                        url = self.current_resource["@controls"]["self"]["href"]
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                        if self.current_resource:
                            self.display_recipe_categories(self.current_resource)
        elif key == 27:
            return

    def remove_recipe_category(self):
        """Remove a category from a recipe"""
        if not self.current_resource or "categories" not in self.current_resource:
            self.display_status("No categories available to remove")
            return
        
        categories = self.current_resource["categories"]
        if not categories:
            self.display_status("No categories to remove")
            return
        
        # Let user select a category
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Category to Remove:", curses.A_BOLD)
        
        for i, category in enumerate(categories):
            name = category.get("name", f"Category {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(categories)+3, 2, f"{len(categories)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(categories):  # 1-n
            selected = categories[key-49]
            
            # Confirm deletion
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
            self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
            self.menu_win.refresh()
            
            confirm = self.menu_win.getch()
            if confirm == ord('y'):
                if "@controls" in selected and "delete" in selected["@controls"]:
                    control = selected["@controls"]["delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    
                    if response is not None:  # Success even if response is empty (204)
                        self.display_status("Category removed successfully")
                        # Refresh the recipe
                        if "@controls" in self.current_resource and "self" in self.current_resource["@controls"]:
                            url = self.current_resource["@controls"]["self"]["href"]
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, url))
                            if self.current_resource:
                                self.display_recipe_categories(self.current_resource)
        elif key == 27:
            return

    def view_recipe_nutrition(self):
        """View nutritional information for a recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to view nutrition for")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "nutritional_info" in selected:
                self.display_nutritional_info(selected["nutritional_info"])
            elif "@controls" in selected and "self" in selected["@controls"]:
                # Fetch the full recipe details if nutritional info isn't included
                url = selected["@controls"]["self"]["href"]
                response = self.make_request("GET", urljoin(BASE_URL, url))
                if response and "nutritional_info" in response:
                    self.display_nutritional_info(response["nutritional_info"])
                else:
                    self.display_status("No nutritional information available")
        elif key == 27:
            return

    def display_nutritional_info(self, nutrition):
        """Display nutritional information"""
        self.clear_content()
        max_y, max_x = self.content_win.getmaxyx()
        
        try:
            self.content_win.addstr(0, 0, "Nutritional Information", curses.A_BOLD)
        except curses.error:
            pass
        
        y = 2
        details = [
            f"Calories: {nutrition.get('calories', 'N/A')} kcal",
            f"Protein: {nutrition.get('protein', 'N/A')} g",
            f"Carbohydrates: {nutrition.get('carbs', 'N/A')} g",
            f"Fat: {nutrition.get('fat', 'N/A')} g"
        ]
        
        for detail in details:
            if y >= max_y - 1:
                break
            try:
                self.content_win.addstr(y, 0, detail)
                y += 1
            except curses.error:
                y += 1
                continue
        
        # Show available controls if there's space
        if "@controls" in nutrition and y < max_y - 2:
            try:
                self.content_win.addstr(y, 0, "Available Actions:", curses.A_BOLD)
                y += 1
                
                for control_name, control in nutrition["@controls"].items():
                    if y >= max_y - 1:
                        break
                        
                    if control_name not in ["self", "profile", "collection", "up"]:
                        try:
                            self.content_win.addstr(y, 2, f"- {control.get('title', control_name)}")
                            y += 1
                        except curses.error:
                            y += 1
                            continue
            except curses.error:
                pass
        
        self.content_win.refresh()
        self.menu_win.getch()
                                                    
    def edit_recipe_nutrition(self):
        """Edit nutritional information for a recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to edit nutrition for")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "nutritional_info" in selected:
                nutrition = selected["nutritional_info"]
                if "@controls" in nutrition and "edit" in nutrition["@controls"]:
                    # Get current values for pre-filling the form
                    current_values = {
                        "calories": nutrition.get("calories", ""),
                        "protein": nutrition.get("protein", ""),
                        "carbs": nutrition.get("carbs", ""),
                        "fat": nutrition.get("fat", ""),
                        "recipe_id": nutrition.get("recipe_id", "")
                    }
                    
                    # Get updated values from user
                    schema = nutrition["@controls"]["edit"].get("schema", {})
                    data = self.get_input_from_schema(schema, current_values)
                    if not data:
                        return  # User cancelled
                    
                    # Make the request
                    control = nutrition["@controls"]["edit"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url, data)
                    
                    if response:
                        self.display_status("Nutritional info updated successfully")
                        # Refresh the recipe list
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
                        if self.current_resource:
                            self.display_recipes(self.current_resource.get("items", []), "Recipes")
            else:
                self.display_status("No nutritional info available to edit")
        elif key == 27:
            return

    def delete_recipe_nutrition(self):
        """Delete nutritional information for a recipe"""
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No recipes available")
            return
        
        recipes = self.current_resource["items"]
        if not recipes:
            self.display_status("No recipes to delete nutrition for")
            return
        
        # Let user select a recipe
        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Recipe:", curses.A_BOLD)
        
        for i, recipe in enumerate(recipes):
            name = recipe.get("food", f"Recipe {i}")
            self.menu_win.addstr(i+2, 2, f"{i+1}. {name}")
        
        self.menu_win.addstr(len(recipes)+3, 2, f"{len(recipes)+1}. Back")
        self.menu_win.refresh()
        
        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(recipes):  # 1-n
            selected = recipes[key-49]
            if "nutritional_info" in selected:
                nutrition = selected["nutritional_info"]
                if "@controls" in nutrition and f"{NAMESPACE}:delete" in nutrition["@controls"]:
                    # Confirm deletion
                    self.menu_win.clear()
                    self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                    self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                    self.menu_win.refresh()
                    
                    confirm = self.menu_win.getch()
                    if confirm == ord('y'):
                        control = nutrition["@controls"][f"{NAMESPACE}:delete"]
                        url = urljoin(BASE_URL, control["href"])
                        response = self.make_request(control["method"], url)
                        
                        if response is not None:  # Success even if response is empty (204)
                            self.display_status("Nutritional info deleted successfully")
                            # Refresh the recipe list
                            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "recipes/"))
                            if self.current_resource:
                                self.display_recipes(self.current_resource.get("items", []), "Recipes")
            else:
                self.display_status("No nutritional info available to delete")
        elif key == 27:
            return

    def get_input_from_schema(self, schema, initial_values=None):
        """Get user input based on a JSON schema with optional initial values"""
        data = {}
        self.clear_content()
        
        if not schema or "properties" not in schema:
            return None
        
        initial_values = initial_values or {}
        required_fields = schema.get("required", [])
        properties = schema["properties"]
        
        y = 0
        for field, config in properties.items():
            prompt = f"Enter {field} ({config.get('type', 'string')}): "
            default_value = str(initial_values.get(field, ""))
            
            self.content_win.addstr(y, 0, prompt)
            self.content_win.addstr(y, len(prompt), default_value)
            self.content_win.refresh()
            
            curses.echo()
            input_str = self.content_win.getstr(y, len(prompt), 50).decode('utf-8')
            curses.noecho()
            
            if not input_str and field in required_fields:
                self.display_status(f"{field} is required!")
                return None
            
            # Convert to appropriate type
            if config.get("type") == "integer":
                try:
                    data[field] = int(input_str) if input_str else None
                except ValueError:
                    self.display_status(f"Invalid integer for {field}")
                    return None
            elif config.get("type") == "number":
                try:
                    data[field] = float(input_str) if input_str else None
                except ValueError:
                    self.display_status(f"Invalid number for {field}")
                    return None
            else:
                data[field] = input_str if input_str else None
            
            y += 2
        
        return data
    
    def nutritional_info_menu(self):
        """Nutritional info management menu"""
        response = self.make_request("GET", urljoin(BASE_URL, "nutritional-info/"))
        if not response:
            return

        self.current_resource = response
        self.display_nutritional_infos(response.get("items", []), "Nutritional Info")

        options = [
            "View Nutritional Info",
            "Add Nutritional Info",
            "Edit Nutritional Info",
            "Delete Nutritional Info",
            "Back"
        ]

        while True:
            self.menu_win.clear()
            self.menu_win.addstr(0, 0, "Nutritional Info Menu", curses.A_BOLD)

            for i, option in enumerate(options):
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. {option}")

            self.menu_win.refresh()

            key = self.menu_win.getch()
            if key == ord('1'):
                self.view_nutritional_info()
            elif key == ord('2'):
                self.add_nutritional_info()
            elif key == ord('3'):
                self.edit_nutritional_info()
            elif key == ord('4'):
                self.delete_nutritional_info()
            elif key == ord('5') or key == 27:
                return

    def display_nutritional_infos(self, infos, title=None):
        self.clear_content()
        if title:
            try:
                self.content_win.addstr(0, 0, title, curses.A_BOLD)
            except curses.error:
                pass

        if not infos:
            try:
                self.content_win.addstr(2, 0, "No nutritional info found")
            except curses.error:
                pass
            self.content_win.refresh()
            return

        max_y, max_x = self.content_win.getmaxyx()
        y = 2

        for info in infos:
            if y >= max_y - 2:
                break
            try:
                self.content_win.addstr(y, 0, f"Recipe {info['recipe_id']} (ID {info['nutritional_info_id']}):")
                self.content_win.addstr(y + 1, 2, f"Calories: {info['calories']} kcal")
                self.content_win.addstr(y + 2, 2, f"Protein: {info['protein']}g | Carbs: {info['carbs']}g | Fat: {info['fat']}g")
                y += 4
            except curses.error:
                y += 1
                continue

        self.content_win.refresh()

    def view_nutritional_info(self):
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No nutritional info available")
            return

        infos = self.current_resource["items"]
        if not infos:
            self.display_status("No data to view")
            return

        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Nutritional Info:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, info in enumerate(infos):
            if i + 2 < max_y:
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. Recipe {info['recipe_id']}")

        back_line = len(infos) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(infos) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(infos):
            selected = infos[key - 49]
            self.display_data(selected, title="Nutritional Info Detail")
            self.menu_win.getch()
        elif key == 27:
            return

    def add_nutritional_info(self):
        if not self.current_resource or "@controls" not in self.current_resource:
            self.display_status("Cannot add - no controls available")
            return

        controls = self.current_resource["@controls"]
        if f"{NAMESPACE}:add-nutritional-info" not in controls:
            self.display_status("Add control not found")
            return

        schema = controls[f"{NAMESPACE}:add-nutritional-info"].get("schema", {})
        data = self.get_input_from_schema(schema)
        if not data:
            return

        control = controls[f"{NAMESPACE}:add-nutritional-info"]
        url = urljoin(BASE_URL, control["href"])
        response = self.make_request(control["method"], url, data)

        if response:
            self.display_status("Nutritional info added successfully")
            self.current_resource = self.make_request("GET", urljoin(BASE_URL, "nutritional-info/"))
            if self.current_resource:
                self.display_nutritional_infos(self.current_resource.get("items", []), "Nutritional Info")

    def edit_nutritional_info(self):
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No data available")
            return

        infos = self.current_resource["items"]
        if not infos:
            self.display_status("No nutritional info to edit")
            return

        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Info to Edit:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, info in enumerate(infos):
            if i + 2 < max_y:
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. Recipe {info['recipe_id']}")

        back_line = len(infos) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(infos) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(infos):
            selected = infos[key - 49]
            if "@controls" in selected and "edit" in selected["@controls"]:
                current_values = {
                    "calories": selected.get("calories", 0),
                    "protein": selected.get("protein", 0),
                    "carbs": selected.get("carbs", 0),
                    "fat": selected.get("fat", 0),
                    "recipe_id": selected.get("recipe_id", 0)
                }
                schema = selected["@controls"]["edit"].get("schema", {})
                data = self.get_input_from_schema(schema, current_values)
                if not data:
                    return

                control = selected["@controls"]["edit"]
                url = urljoin(BASE_URL, control["href"])
                response = self.make_request(control["method"], url, data)

                if response:
                    self.display_status("Updated successfully")
                    self.current_resource = self.make_request("GET", urljoin(BASE_URL, "nutritional-info/"))
                    if self.current_resource:
                        self.display_nutritional_infos(self.current_resource.get("items", []), "Nutritional Info")
        elif key == 27:
            return

    def delete_nutritional_info(self):
        if not self.current_resource or "items" not in self.current_resource:
            self.display_status("No data available")
            return

        infos = self.current_resource["items"]
        if not infos:
            self.display_status("No info to delete")
            return

        self.menu_win.clear()
        self.menu_win.addstr(0, 0, "Select Info to Delete:", curses.A_BOLD)

        max_y, _ = self.menu_win.getmaxyx()
        for i, info in enumerate(infos):
            if i + 2 < max_y:
                self.menu_win.addstr(i + 2, 2, f"{i + 1}. Recipe {info['recipe_id']}")

        back_line = len(infos) + 3
        if back_line < max_y:
            self.menu_win.addstr(back_line, 2, f"{len(infos) + 1}. Back")
        self.menu_win.refresh()

        key = self.menu_win.getch()
        if 49 <= key <= 48 + len(infos):
            selected = infos[key - 49]
            if "@controls" in selected and f"{NAMESPACE}:delete" in selected["@controls"]:
                self.menu_win.clear()
                self.menu_win.addstr(0, 0, "Confirm Deletion:", curses.A_BOLD)
                self.menu_win.addstr(2, 2, "Are you sure? (y/n)")
                self.menu_win.refresh()
                confirm = self.menu_win.getch()
                if confirm == ord('y'):
                    control = selected["@controls"][f"{NAMESPACE}:delete"]
                    url = urljoin(BASE_URL, control["href"])
                    response = self.make_request(control["method"], url)
                    if response is not None:
                        self.display_status("Deleted successfully")
                        self.current_resource = self.make_request("GET", urljoin(BASE_URL, "nutritional-info/"))
                        if self.current_resource:
                            self.display_nutritional_infos(self.current_resource.get("items", []), "Nutritional Info")
        elif key == 27:
            return

def main(stdscr):
    """Main function to run the client"""
    client = FoodManagerClient(stdscr)
    client.main_menu()

if __name__ == "__main__":
    wrapper(main)