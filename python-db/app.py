from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
import csv

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
    """
    @brief This API endpoint function retrieves a list of classes from the database

    A connection to the SQLite database is made, and all records are fetched
    from the classes table, id, section, course_number, and course_title are the attributes
    that are selected and they're returned into a JSON array

    @return A JSON response that contains the list of class objects and a successful
            HTTP status code is returned.
    """
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
    """
    @brief This API endpoint function retrieves information on one class using a specific ID

    @param class_id parameter used to fetch details of a specific class from the db

    @return A JSON response that could contain two possible responses
            200: If a class is found with the specific ID the individual
                classes data is returned along with successful HTTP response (200).
            404: If no class is found with the specific ID a message "Class not found"
                and a 404 error is returned as well.
    """
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
    """
    @brief This API endpoint function retrieves information on a specific class and updates its 
            enrollment 

            The action is stated in the API call in the front end and is taken in by the backend
            and depending on the action (add or remove) the enrollment number of this specific 
            class is incremented or decremented and if successful the new enrollment is returned
            along with a 200 HTTP response

            If the enrollment is over its max it shouldn't be added to so an error occurs and is 
            returned.
            If the enrollment is 0 it shouldn't be removed from so an error occurs and is returned.

    @param class_id parameter used to fetch details of a specific class from the db and update
            them accordingly

    @return A JSON response that could contain two possible responses
            200: If a class is found with the specific ID the individual
                classes data is returned along with successful HTTP response (200).
            404: If no class is found with the specific ID a message "Class not found"
                and a 404 error is returned as well.
    """
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

# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
