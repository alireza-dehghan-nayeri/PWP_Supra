# PWP SPRING 2025
# Food Recipe Managment API
# Group information
* Student 1. Santosh Rokaya: Santosh.rokaya@student.oulu.fi
* Student 2. Fatemeh Soufian Khakestar: Fatemeh.Soufian@student.oulu.fi
* Student 3. Alireza Dehghan Nayeri: Alireza.Dehghan@student.oulu.fi
* Student 4. Ailyah Christopher: ailyah.christopher@student.oulufi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

# PROJECT SETUP

### 1️⃣ Prerequisites
- 🐍 **Python 3.11+** installed

---

### 2️⃣ Setup Instructions

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

# DATABASE SETUP

SQLAlchemy is used for the database which uses sqlite3.

#### 📌 Create the Database
```sh
flask --app food_manager:create_app init-db
```

#### 📌 Add Sample Data
```sh
flask --app food_manager:create_app sample-data
```

#### 📌 Interact with Database
```sh
flask --app food_manager:create_app shell
Food.query.all()
Recipe.query.all()
Ingredient.query.all()
Category.query.all()
NutritionalInfo.query.all()
```

#### 📌 Dump the Database into .sql File
```sh
cd instance
sqlite3 food-manager.db .dump > dump.sql
```
#### 📌 Run the Flask App
```sh
flask --app food_manager:create_app run 
Hit the Url with Prefix: /api/ 
e.g http://127.0.0.1:5000/api/foods/
```

#### 📌 Clearing the Database Without Dropping Tables (if needed)
```sh
flask --app food_manager:create_app clear-db
```

### 3️⃣ Run PyTest Instructions

#### 📌 Set PyTest Path to the Current Root Directory
```sh
export PYTHONPATH=$(pwd)
```

#### 📌 Run all the PyTest Cases for each API
```sh
pytest -v tests/api_test.py  
```


