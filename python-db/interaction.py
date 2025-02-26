import sqlite3
#Instructions:
# WSL - sudo apt install sqlite3

# connect to the database via the conenct command, specify db name
main_database = sqlite3.connect("test.db")
# set up a cursor for executing commands 
cursor = main_database.cursor()

# provide the command and execute it 
cursor.execute("SELECT * from test")

# fetch result and loop to print all the rows in the table
db_rows = cursor.fetchall()
for i in db_rows:
    print(i)

# close connection
main_database.close()