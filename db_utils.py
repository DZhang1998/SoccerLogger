"""
File is designed to interact with database
"""
import mysql.connector
   
# Login database connection
# User only has SELECT, INSERT, UPDATE permissions
login_database = {
    "host": "usersrv01.cs.virginia.edu",
    "user": "man9ej_a",
    "password": "Spr1ng2021!!",
    "database": "man9ej_login"
}

# superuser = {
#     "host": "usersrv01.cs.virginia.edu",
#     "user": "man9ej",
#     "password": "Fall2021!!",
#     "database": "man9ej_final_project"
# }

# Project database connections - switch to this after login
project_database = {
    "host": "usersrv01.cs.virginia.edu",
    "user": "man9ej_b",
    "password": "Spr1ng2021!!",
    "database": "man9ej_final_project"
}

# How to connect to the database
db = mysql.connector.connect(**login_database)

# Switch database back to login database
def switch_db_to_login():
    global db

    if db.database == login_database["database"]:
        return

    # Connect to login database
    db = mysql.connector.connect(**login_database)

def switch_db_to_project():
    global db

    if db.database == project_database["database"]:
        return
    
    # Connect to login database
    db = mysql.connector.connect(**project_database)
