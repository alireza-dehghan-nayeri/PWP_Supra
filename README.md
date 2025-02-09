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
#### 📌 Run the App
```sh
flask run
```

# DATABASE SETUP

SQLAlchemy is used for the database which uses sqlite3.

#### 📌 Create the Database
```sh
flask init-db
```

#### 📌 Add Sample Data
```sh
flask sample-data
```

#### 📌 Interact with Database
```sh
flask shell
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

#### 📌 Clearing the Database Without Dropping Tables (if needed)
```sh
flask clear-db
```
