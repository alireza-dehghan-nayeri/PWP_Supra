PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE food (
	food_id INTEGER NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	description VARCHAR(255), 
	image_url VARCHAR(255), 
	PRIMARY KEY (food_id), 
	UNIQUE (name)
);
INSERT INTO food VALUES(1,'Pizza','Italian flatbread topped with various ingredients',NULL);
INSERT INTO food VALUES(2,'Pasta','Italian noodles with sauce',NULL);
INSERT INTO food VALUES(3,'Salad','Fresh mixed vegetables with dressing',NULL);
INSERT INTO food VALUES(4,'Soup','Warm liquid food with various ingredients',NULL);
CREATE TABLE ingredient (
	ingredient_id INTEGER NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	image_url VARCHAR(255), 
	PRIMARY KEY (ingredient_id), 
	UNIQUE (name)
);
INSERT INTO ingredient VALUES(1,'Flour','flour.jpg');
INSERT INTO ingredient VALUES(2,'Tomato','tomato.jpg');
INSERT INTO ingredient VALUES(3,'Cheese','cheese.jpg');
INSERT INTO ingredient VALUES(4,'Basil','basil.jpg');
INSERT INTO ingredient VALUES(5,'Olive Oil','olive_oil.jpg');
INSERT INTO ingredient VALUES(6,'Garlic','garlic.jpg');
INSERT INTO ingredient VALUES(7,'Salt','salt.jpg');
INSERT INTO ingredient VALUES(8,'Pepper','pepper.jpg');
CREATE TABLE category (
	category_id INTEGER NOT NULL, 
	name VARCHAR(64) NOT NULL, 
	description VARCHAR(255), 
	PRIMARY KEY (category_id), 
	UNIQUE (name)
);
INSERT INTO category VALUES(1,'Italian','Traditional Italian cuisine');
INSERT INTO category VALUES(2,'Vegetarian','Meat-free dishes');
INSERT INTO category VALUES(3,'Quick & Easy','Ready in 30 minutes or less');
INSERT INTO category VALUES(4,'Healthy','Nutritious and balanced meals');
CREATE TABLE recipe (
	recipe_id INTEGER NOT NULL, 
	food_id INTEGER NOT NULL, 
	instruction VARCHAR(255) NOT NULL, 
	prep_time INTEGER NOT NULL, 
	cook_time INTEGER NOT NULL, 
	servings INTEGER NOT NULL, 
	PRIMARY KEY (recipe_id), 
	CONSTRAINT prep_time_constraint CHECK (prep_time >= 0), 
	CONSTRAINT cook_time_constraint CHECK (cook_time >= 0), 
	CONSTRAINT servings_constraint CHECK (servings > 0), 
	FOREIGN KEY(food_id) REFERENCES food (food_id) ON DELETE CASCADE
);
INSERT INTO recipe VALUES(1,1,replace('1. Make dough with flour, water, and yeast\n2. Spread tomato sauce\n3. Add fresh mozzarella and basil\n4. Bake at 450°F for 15 minutes','\n',char(10)),30,15,4);
INSERT INTO recipe VALUES(2,2,replace('1. Cook pasta in salted water\n2. Sauté garlic in olive oil\n3. Toss pasta with garlic oil\n4. Add cheese and pepper','\n',char(10)),10,15,2);
CREATE TABLE nutritional_info (
	nutritional_info_id INTEGER NOT NULL, 
	recipe_id INTEGER NOT NULL, 
	calories INTEGER NOT NULL, 
	protein FLOAT NOT NULL, 
	carbs FLOAT NOT NULL, 
	fat FLOAT NOT NULL, 
	PRIMARY KEY (nutritional_info_id), 
	CONSTRAINT calories_constraint CHECK (calories >= 0), 
	CONSTRAINT protein_constraint CHECK (protein >= 0), 
	CONSTRAINT carbs_constraint CHECK (carbs >= 0), 
	CONSTRAINT fat_constraint CHECK (fat >= 0), 
	UNIQUE (recipe_id), 
	FOREIGN KEY(recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE
);
INSERT INTO nutritional_info VALUES(1,1,266,11.0,33.0,9.0);
INSERT INTO nutritional_info VALUES(2,2,320,9.0,42.0,14.0);
CREATE TABLE recipe_ingredient (
	recipe_id INTEGER NOT NULL, 
	ingredient_id INTEGER NOT NULL, 
	quantity FLOAT NOT NULL, 
	unit VARCHAR(64) NOT NULL, 
	PRIMARY KEY (recipe_id, ingredient_id), 
	CONSTRAINT quantity_constraint CHECK (quantity > 0), 
	FOREIGN KEY(recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE, 
	FOREIGN KEY(ingredient_id) REFERENCES ingredient (ingredient_id) ON DELETE CASCADE
);
INSERT INTO recipe_ingredient VALUES(1,1,500.0,'g');
INSERT INTO recipe_ingredient VALUES(1,2,200.0,'g');
INSERT INTO recipe_ingredient VALUES(1,3,150.0,'g');
INSERT INTO recipe_ingredient VALUES(1,4,10.0,'leaves');
INSERT INTO recipe_ingredient VALUES(1,5,2.0,'tbsp');
INSERT INTO recipe_ingredient VALUES(2,6,4.0,'cloves');
INSERT INTO recipe_ingredient VALUES(2,5,3.0,'tbsp');
INSERT INTO recipe_ingredient VALUES(2,3,50.0,'g');
INSERT INTO recipe_ingredient VALUES(2,7,1.0,'tsp');
INSERT INTO recipe_ingredient VALUES(2,8,0.5,'tsp');
CREATE TABLE recipe_category (
	recipe_id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	PRIMARY KEY (recipe_id, category_id), 
	FOREIGN KEY(recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE, 
	FOREIGN KEY(category_id) REFERENCES category (category_id) ON DELETE CASCADE
);
INSERT INTO recipe_category VALUES(1,1);
INSERT INTO recipe_category VALUES(1,2);
INSERT INTO recipe_category VALUES(2,1);
INSERT INTO recipe_category VALUES(2,3);
COMMIT;
