# Food Recipe Management API
## Group information
* Student 1. Santosh Rokaya: Santosh.rokaya@student.oulu.fi
* Student 2. Fatemeh Soufian Khakestar: Fatemeh.Soufian@student.oulu.fi
* Student 3. Alireza Dehghan Nayeri: Alireza.Dehghan@student.oulu.fi
* Student 4. Ailyah Christopher: ailyah.christopher@student.oulufi


<!-- __Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to set up and run the client, instructions on how to set up and run the auxiliary service and instructions on how to deploy the api in a production environment__ -->

## PROJECT SETUP

### Prerequisites
- 🐍 **Python 3.11+**

### Setup Instructions

#### 📌 Clone the Repository
```sh
git clone https://github.com/alireza-dehghan-nayeri/PWP_Supra.git
cd PWP_Supra
```

#### 📌 Create and Activate a Virtual Environment
```sh
python -m venv venv
```
**Windows:**
```sh
venv\Scripts\activate
```
**Mac/Linux:**
```sh
source venv/bin/activate
```

#### 📌 Install Required Dependencies
```sh
pip install -r requirements.txt
```

#### 📌 Move to the `food_manager` Directory
```sh
cd food_manager
```

#### 📌 Create the Database

SQLAlchemy is used for the database which uses sqlite3.

```sh
flask --app food_manager:create_app init-db
```

#### 📌 Add Sample Data
```sh
flask --app food_manager:create_app sample-data
```

#### 📌 (optional) Interact with Database
```sh
flask --app food_manager:create_app shell
Food.query.all()
Recipe.query.all()
Ingredient.query.all()
Category.query.all()
NutritionalInfo.query.all()
```

#### 📌 (optional) Dump the Database into .sql File
```sh
cd instance
sqlite3 food-manager.db .dump > dump.sql
```

#### 📌 Run the Flask App
```sh
flask --app food_manager:create_app run 
```
Hit the Url with Prefix: /api/ e.g., http://127.0.0.1:5000/api/foods/

#### 📌 Running Api Docs
```sh
flask --app food_manager:create_app run 
```
Hit the Url with Prefix: http://127.0.0.1:5000/apidocs/#/

#### 📌 (if needed) Clearing the Database Without Dropping Tables
```sh
flask --app food_manager:create_app clear-db
```

## Run PyTest Instructions

#### 📌 Set PyTest Path to the Current Root Directory
```sh
export PYTHONPATH=$(pwd)
```

#### 📌 Run all the PyTest Cases for each API
```sh
pytest -v tests/test_api.py  
```
#### 📌 Output the Test Coverage
```sh
pytest --cov=food_manager --cov-report=html     
```

## Run PyLint Instructions

#### 📌 Run PyLint for all files in the food_manager directory
```sh
pylint --disable=no-member,import-outside-toplevel,no-self-use ./food_manager
```


