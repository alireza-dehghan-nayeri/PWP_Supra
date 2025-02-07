# PWP SPRING 2025
# PROJECT NAME
# Group information
* Student 1. Santosh Rokaya: Santosh.rokaya@student.oulu.fi
* Student 2. Fatemeh Soufian Khakestar: Fatemeh.Soufian@student.oulu.fi
* Student 3. Alireza Dehghan Nayeri: Alireza.Dehghan@student.oulu.fi
* Student 4. Ailyah Christopher: ailyah.christopher@student.oulufi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

# PROJECT SETUP
CONTENTS:
1. Prerequisites
2. Setup Instructions

-----------------------------------------------------
1) PREREQUISITES
    - Python 3.11+ installed

-----------------------------------------------------
2) Setup Instructions
-----------------------------------------------------
1. CLONE THE REPOSITORY
    - git clone <REPO_URL>
    - cd <PROJECT_FOLDER>

2. CREATE AND ACTIVATE A VIRTUAL ENVIRONMENT 
    - python -m venv venv
   # Windows:
    - venv\Scripts\activate
   # Mac/Linux:
    - source venv/bin/activate

3. INSTALL REQUIRED DEPENDENCIES
    - pip install -r requirements.txt

4. Move to Directory food_recipe
    - Open terminal and run command: 
         - cd food_recipe

5. Create Database
    - In the terminal run command: 
         - flask init-db

6. Add Sample Data
    - In the terminal run command: 
         - flask sample-data

7. Clearing the Database Without Dropping the Tables (if needed)
    - In the terminal run command: 
         - flask clear-db





