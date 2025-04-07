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
    """
    Retrieve a list of classes from the database.

    A connection to the SQLite database is established, and all records are fetched 
    from the ``classes`` table. The attributes fetched are ``id``, ``section``, 
    ``course_number``, and ``course_title``. These are returned as a JSON array.

    :return: JSON response containing the list of class objects along with an HTTP 200 status.
    :rtype: flask.Response
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
    Retrieve information about a single class using its numeric ID.

    Args:
        class_id (int): 
            The ID of the class to fetch from the database.

    Returns:
        flask.Response: 
            A JSON response with two possible outcomes:
            
            * **200 OK** – If the class is found, returns a JSON object of class data.
            * **404 Not Found** – If the class is not found, returns a JSON error message.
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
    """
    Upload and process a CSV file.

    .. note::
        Expects a form field named ``file``.

    :return: JSON response indicating success or failure.
    :rtype: flask.Response
    """
    # check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)  # Save file in uploads folder

    # Parse CSV file
    try:
        file_path = fix_csv(file_path) # Function call to fix the sheet for trailing commas
        create_tables() # Create the tables in the database
        course_data = parse_csv(file_path)  # Parse the CSV file
        insert_csv_into_table(course_data) # Insert the parsed data into the database
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200

def create_tables():
    """
    Create the ``classes`` table in the database.

    If it exists, it is dropped before re-creation.
    """
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
    """
    Insert parsed CSV data into the ``classes`` table.

    :param course_data: List of dictionaries with course info.
    :type course_data: list
    """
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

'''Function to fix the trailing commas in the csv'''
def fix_csv(csv_document):
    '''Cannot open the same file for input and output to write, take the extension and and -fix to it to have two separate files'''
    fixed_csv = csv_document.replace(".csv", "-fix.csv")
    '''Open the csv doc and the output file temporarily created'''
    with open(csv_document, 'r', newline='') as csv_to_clean, open(fixed_csv, 'w', newline='') as output_csv:
        reader = csv.reader(csv_to_clean)
        writer = csv.writer(output_csv)
        '''Loop to check if the last part of the row is empty and delete appropriately'''
        for row in reader:
            while row and row[-1] == '':
                row.pop()
            writer.writerow(row)
        '''Return fixed sheet'''
    return fixed_csv
    

def parse_csv(csv_document):
    """
    Parse the CSV file and return structured course data.

    Skips the first two lines before reading headers.

    :param csv_document: Path to the CSV file.
    :type csv_document: str
    :return: List of dictionaries representing each course entry.
    :rtype: list
    """
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
    Update enrollment for a specific class by ID.

    Increments or decrements the enrollment number according to the request 
    (``add`` or ``remove``). If the maximum capacity is reached, adding is not allowed. 
    If enrollment is zero, removing is not allowed.

    :param class_id: ID of the class to update.
    :type class_id: int

    :return: JSON response containing the updated enrollment or an error message.
    :rtype: flask.Response

    :status 200: Class found and enrollment updated successfully.
    :status 400: Invalid update (e.g., class is full or empty).
    :status 404: Class not found.
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

@app.route("/export")
def export_to_csv():
    """
    Export classes from the database into a CSV file named ``output.csv``.

    Reads data from the existing CSV (referenced by ``file_path``) and updates
    enrollment values using the database. Ensures the first row is the term,
    the second row is the generation date/time, and subsequent rows contain
    updated class info.

    :return: JSON response indicating success or an error message.
    :rtype: flask.Response

    :status 200: Successfully exported data to file.
    :status 404: No database or error accessing records.
    """
    conn = sqlite3.connect(DB_FILE)
    # check to make sure the connection worked
    # likely will remove this later. I'm thinking we disable the button if theres no database/problems if possible
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes")

        # the idea here is to go line by line and copy each line into a list. 
        # if there's something in the first list, process depending on where it is (date, class name, etc.)
        # if not, process new student count (since data lines have their first csv data empty)
        with open(file_path, "r", encoding="utf-8") as in_file:
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
