from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
import csv
import datetime

# Little overview of the imports above (uses):
# flask → Web framework
# flask-cors → Allows Vue to communicate with Flask
# flask-sqlalchemy → ORM for SQLite
# pandas → CSV parsing

app = Flask(__name__)
# Allow frontend requests using CORS from any origin
CORS(app, supports_credentials=True)

# Our SQLite database file
DB_FILE = "database.db"
# Document Uploads file
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure uploads directory exists

@app.route("/classes", methods=["GET"])
def get_classes():
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()

    cursor.execute("SELECT id, section, course_number, course_title FROM classes")
    rows = cursor.fetchall()
    conn.close()

    # Serialize the data
    classes = []
    for row in rows:
        class_data = {
            "id": row[0],
            "section": row[1],
            "courseName": row[2],
            "courseTitle": row[3], 
        }
        classes.append(class_data)

    return jsonify(classes), 200

# API Route to fetch class details by ID 
@app.route("/class/<int:class_id>", methods=["GET"])
def get_class(class_id):
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
    # fetch just one row as theres only one class per id
    row = cursor.fetchone()
    conn.close()

    if row:
        class_data = {
            "id": row[0],
            "term": row[1],
            "courseName": row[2],
            "section": row[3],
            "name": row[4],  # Course Title
            "room": row[5],
            "time": row[6],
            "currentEnrollment": row[7],
            "maxEnrollment": row[8]
        }
        # serialize and return class data if class is found
        return jsonify(class_data), 200
    else:
        # otherwise provide a 404 error and message along with it 
        return jsonify({"message": "Class not found"}), 404

# API Route to receive and handle CSV importing
@app.route('/upload', methods=['POST'])
def upload_file():

    # check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)  # Save file in uploads folder
    imported_file = file_path

    # Parse CSV file
    try:
        create_tables() # Create the tables in the database
        course_data = parse_csv(file_path)  # Parse the CSV file
        insert_csv_into_table(course_data) # Insert the parsed data into the database
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200

def create_tables():
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop the 'classes' table if it exists
    cursor.execute("DROP TABLE IF EXISTS classes")

    # Now, create the 'classes' table
    cursor.execute("""
        CREATE TABLE classes (
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
    conn.close()


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


def parse_csv(csv_document):
    course_data = []
    relevant_columns = ["Term", "Course", "Section #", "Course Title", "Room", "Meeting Pattern", "Enrollment", "Maximum Enrollment"]

    # Read and process csv file
    with open(csv_document, mode='r', encoding='utf-8') as infile:
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

        
# API Route to update enrollment for a class
@app.route("/class/<int:class_id>/update-enrollment", methods=["POST"])
def update_enrollment(class_id):
    data = request.get_json()
    action = data.get("action")

    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()
    cursor.execute("SELECT enrollment, max_enrollment FROM classes WHERE id = ?", (class_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"message": "Class not found"}), 404
    
    enrollment, max_enrollment = row

    if action == "add":
        if enrollment < max_enrollment:
            enrollment += 1
        else:
            conn.close()
            return jsonify({"message": "Class is full"}),
    elif action == "remove":
        if enrollment > 0:
            enrollment -= 1
        else:
            conn.close()
            return jsonify({"message": "Class is empty"}), 400
        
    cursor.execute("UPDATE classes SET enrollment = ? WHERE id = ?", (enrollment, class_id))
    conn.commit()
    conn.close()

    return jsonify({"enrollment": enrollment}), 200

@app.route("/export")
def export_to_csv():
    conn = sqlite3.connect(DB_FILE)
    # check to make sure the connection worked
    # likely will remove this later. I'm thinking we disable the button if theres no database/problems if possible
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes")

        # currently I'm relying on the input csv file to read all the excess data from to make a perfect copy of the file, with the changes that were made
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Adjust if needed
        data_dir = os.path.join(repo_root, "Team5-PKI_Scheduler\\my-vue-app\\")
        input_file = os.path.join(data_dir, "Spring2023.csv")

        # the idea here is to go line by line and copy each line into a list. 
        # if there's something in the first list, process depending on where it is (date, class name, etc.)
        # if not, process new student count (since data lines have their first csv data empty)
        with open(input_file, "r", encoding="utf-8") as in_file:
            reader = csv.reader(in_file)

            # start overwriting the csv file. start with writing the date
            data = next(reader)
            season, year = data[0].split(' ')
            with open("output.csv", "w", newline='', encoding="utf-8") as out_file:
                writer = csv.writer(out_file, quoting=csv.QUOTE_NOTNULL)
                writer.writerow([f'{season} {year}'])

            # append date, then column headers
            with open("output.csv", "a", newline='', encoding="utf-8") as out_file:
                next(reader) # skip date in the input
                writer = csv.writer(out_file, quoting=csv.QUOTE_NOTNULL)

                date = datetime.datetime.now()
                # stripping leading zeroes off the current month, day, and hour
                month = date.strftime("%m").lstrip('0')
                day = date.strftime("%d").lstrip('0')
                hour = date.strftime("%I").lstrip('0')
                data = [f'Generated {month}/{day}/{date.strftime("%Y")}, {hour}{date.strftime(":%M:%S %p")}']
                writer.writerow(data) # write date

                data = next(reader)
                data[0] = None # first column doesn't get quoted
                writer.writerow(data) # write headers 

            # start writing in all the new data
            id = 1 # this is assuming we don't delete or rearrange class IDs
            for row in reader:
                if len(row) > 1: # process new data
                    with open("output.csv", "a", newline='', encoding="utf-8") as out_file:
                        writer = csv.writer(out_file, quoting=csv.QUOTE_NOTNULL)

                        # data is whatever's in the input csv file
                        data = row
                        new_enrollment_count = cursor.execute("SELECT enrollment FROM classes WHERE id = ?", (id,))
                        data[0] = None # so it doesn't get quoted in the csv file
                        data[28] = new_enrollment_count # 28 is the index of the current enrollment count. if there's a more dynamic way to do this in case the data format changes, let's do that instead

                        writer.writerow(data)
                        id += 1
                else: # copy row
                    with open("output.csv", "a", newline='', encoding="utf-8") as out_file:
                        writer = csv.writer(out_file, quoting=csv.QUOTE_NOTNULL)
                        writer.writerow(row)

    except Exception:
        return jsonify("No database exists"), 404
    finally:
        conn.close()
    print("Successfully exported data to file")
    return jsonify('Successfully exported data to file'), 200
    
# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
