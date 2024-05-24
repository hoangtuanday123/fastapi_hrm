# import pyodbc

# def connection():
#     s = 'DESKTOP-KEFRDN4' #Your server name 
#     d = 'project_flask' 
#     u = '' #Your login
#     p = '' #Your login password
#     cstr = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={s};DATABASE={d};Trusted_Connection=yes;'
#     conn = pyodbc.connect(cstr)
#     return conn

import mysql.connector
def connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Tuan0843055059#",
        database="project_flask"
    )