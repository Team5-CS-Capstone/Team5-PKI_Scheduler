import sqlite3
import csv
import os

# Get the directory where the script is running
script_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate up to the repository root (assuming script is inside the repo)
repo_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Adjust if needed

# Define the relative path to the data file inside the repo
data_dir = os.path.join(repo_root, "Team5-PKI_Scheduler\\my-vue-app\\")
input_file = os.path.join(data_dir, "Spring2023.csv")

# Define the relevant columns we need
relevant_columns = ["Term", "Section #", "Course Title", "Room", "Meeting Pattern", "Enrollment", "Maximum Enrollment"]

# Check if file exists
if not os.path.exists(input_file):
    raise FileNotFoundError(f'File not found: {input_file}')

# Lists to store categorized data from csv pull
term_list = []
section_list = []
course_title_list = []
room_list = []
meeting_pattern_list = []
enrollment_list = []
max_enrollment_list = []

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

    # Store data into separate lists
    for row in reader:
        # Ensure row has enough columns before storing
        if len(row) >= max(col_indexes.values()) + 1:
            term_list.append(row[col_indexes["Term"]])
            section_list.append(row[col_indexes["Section #"]])
            course_title_list.append(row[col_indexes["Course Title"]])
            room_list.append(row[col_indexes["Room"]])
            meeting_pattern_list.append(row[col_indexes["Meeting Pattern"]])
            enrollment_list.append(row[col_indexes["Enrollment"]])
            max_enrollment_list.append(row[col_indexes["Maximum Enrollment"]])

# Store the categorized lists in a dictionary for easy access
course_data = {
    "Term": term_list,
    "Section #": section_list,
    "Course Title": course_title_list,
    "Room": room_list,
    "Meeting Pattern": meeting_pattern_list,
    "Enrollment": enrollment_list,
    "Maximum Enrollment": max_enrollment_list,
}

# Print all lists
for key, values in course_data.items():
    print(f"{key}:")
    for value in values:
        print(f"{value}")

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