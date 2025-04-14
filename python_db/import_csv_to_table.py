import sqlite3
import csv
import os
from utils import parse_instructor

# Create the SQLite table for storing this parsed information
def create_table():
    # Creation of connection to the DB
    conn = sqlite3.connect(DB_FILE)
    # cursor is needed in order to execute SQLite commands
    cursor = conn.cursor()

    # Create the 'classes' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            course_number TEXT,
            section TEXT,
            course_title TEXT,
            room TEXT,
            meeting_pattern TEXT,
            enrollment INTEGER,
            max_enrollment INTEGER
        )
    """)

    conn.commit()  # Save changes
    conn.close()   # Close the connection


def insert_csv_into_table(course_data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # for entry in course_data:
    for entry in course_data:
        cursor.execute("""
            INSERT INTO classes (term, course_number, section, course_title, room, meeting_pattern, enrollment, max_enrollment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (entry['Term'], entry['Course'], entry['Section #'], entry['Course Title'], entry['Room'], entry['Meeting Pattern'], 
                int(entry['Enrollment']), int(entry['Maximum Enrollment'])))

    conn.commit()
    conn.close()

    print("Data should now properly be inserted into the database from the csv file")

# Somehow here we will provide the parameter with the proper csv 
# document that we want to parse from the frontend on import click
# and we can later create another function for the 
# exporting of csv files in proper format and just call that from
# the front end
def parse_csv(csv_document):
    course_data = []

    # Read and process csv file
    with open(input_file, mode='r', encoding='utf-8') as infile:
        reader = csv.reader(infile)

        # Skip first two lines (extra headers)
        next(reader)
        next(reader)

        # Read the actual headers
        headers = next(reader)

        # Get the indexes of the relevant columns
        col_indexes = {col: headers.index(col) for col in relevant_columns}

        # Read and store rows as dictionaries
        for row in reader:
            # Ensure row has enough columns before storing
            if len(row) >= max(col_indexes.values()) + 1:
                # appends information into a list of 
                # dictionaries per class entry
                course_data.append({
                    "Term": row[col_indexes["Term"]],
                    "Course": row[col_indexes["Course"]],
                    "Section #": row[col_indexes["Section #"]],
                    "Course Title": row[col_indexes["Course Title"]],
                    "Room": row[col_indexes["Room"]],
                    "Meeting Pattern": row[col_indexes["Meeting Pattern"]],
                    "Enrollment": int(row[col_indexes["Enrollment"]]),  # Convert to int
                    "Maximum Enrollment": int(row[col_indexes["Maximum Enrollment"]])
                })
    
    # Returns a list of dicts (one dict per class entry)
    return course_data

# Print all lists
# for key, values in course_data.items():
#     print(f"{key}:")
#     for value in values:
#         print(f"{value}")

# # Print each dictionary item one at a time
# for i in range(len(term_list)):
#     # Creates a dictionary for each course_data entry  
#     entry = {key: values[i] for key, values in course_data.items()}
#     print(entry)  

# #Instructions:
# # WSL - sudo apt install sqlite3

# # connect to the database via the conenct command, specify db name
# main_database = sqlite3.connect("test.db")
# # set up a cursor for executing commands 
# cursor = main_database.cursor()

# # provide the command and execute it 
# cursor.execute("SELECT * from test")

# # fetch result and loop to print all the rows in the table
# db_rows = cursor.fetchall()
# for i in db_rows:
#     print(i)

# # close connection
# main_database.close()

# Start of script
if __name__ == "__main__":
    # Get the directory where the script is running
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Navigate up to the repository root (assuming script is inside the repo)
    repo_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Adjust if needed

    # Define the relative path to the data file inside the repo
    data_dir = os.path.join(repo_root, "Team5-PKI_Scheduler\\my-vue-app\\")
    input_file = os.path.join(data_dir, "Spring2023.csv")

    DB_FILE = "database.db"

    # Define the relevant columns we need
    relevant_columns = ["Term", "Course", "Section #", "Course Title", "Room", "Meeting Pattern", "Enrollment", "Maximum Enrollment"]

   
    # Check if file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f'File not found: {input_file}')
    
    create_table()  # Ensure database & table exist
    course_data = parse_csv(input_file)  # Parse CSV
    insert_csv_into_table(course_data)  # Insert into SQLite