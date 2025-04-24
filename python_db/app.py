from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
import csv
import datetime

# Importing utility functions from utils.py
from utils import parse_instructor, get_or_create_professor, fix_csv

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

@app.route("/class/<int:class_id>/possible-reassignments", methods=["GET"])
def get_possible_reassignments(class_id):
    """
    Retrieve possible reassignments for a specific class.

    :param class_id: ID of the class to fetch possible reassignments for.
    :type class_id: int

    :return: JSON response containing the list of possible reassignments.
    :rtype: flask.Response
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Enable row factory to access columns by name
    cursor = conn.cursor()

    cursor.execute("""
        WITH target_class AS (
                    SELECT id, meeting_pattern, enrollment,
                    max_enrollment, room, course_number, course_title
                    FROM classes
                    WHERE id = ?
                )
                    SELECT b.*
                    FROM classes b, target_class t
                    WHERE b.id != t.id
                    AND b.meeting_pattern = t.meeting_pattern -- same meeting times
                    AND t.max_enrollment >= b.enrollment -- target class can accommodate the other class
                    AND b.max_enrollment >= t.enrollment -- other class can accommodate the target class
                    AND  NOT (b.enrollment = 0 AND b.max_enrollment = 0) -- ignore classes with no enrollment (they're remote classes)
                ORDER BY (b.max_enrollment - b.enrollment) ASC -- sort by available seats
    """, (class_id,))
    partners = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify(partners), 200

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

    cursor.execute("SELECT id, section, course_number, course_title, enrollment, max_enrollment FROM classes")
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
            "currentEnrollment": row[4],
            "maxEnrollment": row[5],
        }
        classes.append(class_data)

    return jsonify(classes), 200

@app.route("/class/<int:class_id>/professors", methods=["GET"])
def get_professors(class_id):
    """
    Retrieve the professors associated with a specific class.

    :param class_id: ID of the class to fetch professors for.
    :type class_id: int

    :return: JSON response containing the list of professors for the specified class.
    :rtype: flask.Response
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT professors.id, professors.first_name, professors.last_name, professors.p_id
        FROM professors
        JOIN class_professors ON professors.id = class_professors.professor_id
        WHERE class_professors.class_id = ?
    """, (class_id,))

    rows = cursor.fetchall()
    conn.close()

    professors = []
    for row in rows:
        professors.append({
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "p_id": row[3]
        })

    return jsonify(professors), 200

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
    class_data = get_class_details(class_id)
    if class_data:
        # serialize and return class data if class is found
        return jsonify(class_data), 200
    else:
        # otherwise provide a 404 error and message along with it 
        return jsonify({"message": "Class not found"}), 404
    
def get_class_details(class_id):
    """
    A helper function that returns class details.

    Args:
        class_id (int):
            The ID of the class to fetch from the database.

    Returns:
        dict:
            A dictionary of class details.
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
        return class_data
    else:
        return None

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
    global file_path # make sure the file path is global so we can access it later
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
    
    # Delete the temp fixed csv file and the original csv file from uploads folder
    os.remove(file_path)
    os.remove(file_path.replace("-fix", ""))
    
    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200

def create_tables():
    """
    Create the ``classes`` table in the database.

    If it exists, it is dropped before re-creation.
    """
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()

    # Drop the 'classes' table if it exists
    cursor.execute("DROP TABLE IF EXISTS classes")
    cursor.execute("DROP TABLE IF EXISTS professors")
    cursor.execute("DROP TABLE IF EXISTS class_professors")

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
            max_enrollment INTEGER,
            professor_id INTEGER,
            UNIQUE (term, course_number, section)
        )
    """)

    # Create the 'professors' table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS professors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                p_id TEXT
            )
        """)
    
    # Create the 'class_professors' table for many-to-many relationship
    # between classes and professors
    cursor.execute("""CREATE TABLE IF NOT EXISTS class_professors (
            class_id INTEGER,
            professor_id INTEGER,
            FOREIGN KEY (class_id) REFERENCES classes(id),
            FOREIGN KEY (professor_id) REFERENCES professors(id)
            UNIQUE (class_id, professor_id)
        )"""
    )

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

    # Start the crosslist checking and generating the dictionary dynamically based on if a class is crosslisted
    cross_lists = {}
    # Loop & check if a class is cross listed
    for entry in course_data:
        cross_list = entry.get("Cross-listings", "").strip()
        if cross_list:
            # reconstructing the key, take out spaces and split them with the "/", reconstruct to make sure everything works fine
            courses = [course_num.strip() for course_num in cross_list.split('/')]
            cross_list_key = " / ".join(sorted(courses))
            # If there is a crosslist in the column and the key is not in the dictionary
            if cross_list_key not in cross_lists:
                #add it
                cross_lists[cross_list_key] = []
            cross_lists[cross_list_key].append(entry["Course"])

    # for entry in course_data:
    # added some crosslist stuff here to check if it is in the dictionary generated from above
    for entry in course_data:
        # Info to get to see if crosslisted
        course = entry["Course"]
        cross_list = entry.get("Cross-listings", "").strip()
        if cross_list:
            # same key stuff as above, just re constructing so the keys are universal
            courses = [course_num.strip() for course_num in cross_list.split('/')]
            cross_list_key = " / ".join(sorted(courses))
        # This is where the check is to see if the class is 1- Cross listed in the column is a key in the dictionary, 2- if the course is a value in the key
        if cross_list_key in cross_list and course in cross_lists[cross_list_key]:
            # List to get which courses are crosslisted under one particular key, loop through course data once again and get all the courses and check each one to see if it is a course in one particular key
            group_crosslists = []
            for cross_list_entry in course_data:
                if cross_list_entry["Course"] in cross_lists[cross_list_key]:
                    group_crosslists.append(cross_list_entry)
            # Take account all of enrollment and sum them up together, but this time looping through that list of all the course under one particular key
            total_enrollment = sum(int(course["Enrollment"]) for course in group_crosslists)
            total_max = sum(int(course["Maximum Enrollment"]) for course in group_crosslists)
            # To properly get the sqlite statement
            grouped_class = group_crosslists[0]
            # There is an ignore statement as since the primary key was changed, it will error if it finds a duplicate, IGNORE will ignore the duplicates
            cursor.execute("""INSERT OR IGNORE INTO classes (term, course_number, section, course_title, room, meeting_pattern, enrollment, max_enrollment) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (grouped_class['Term'], cross_list_key, grouped_class['Section #'], grouped_class['Course Title'], grouped_class['Room'], grouped_class['Meeting Pattern'], total_enrollment, grouped_class["Cross-list Maximum"]))

            # Get the newest class ID
            class_id = cursor.lastrowid

            # Parse intstructor from csv and get needed info for adding to database
            results = parse_instructor(grouped_class['Instructor'])

            for professor_dict in results:
                first_name = professor_dict['first_name']
                last_name = professor_dict['last_name']
                professor_id = professor_dict['p_id']

                # Insert the class-professor relationship into the class_professors table and 
                # add the professor to the database if they don't exist
                get_or_create_professor(cursor, first_name, last_name, professor_id, class_id)
        else:
            # Insert non crosslisted class into the database
            cursor.execute("""
                INSERT OR IGNORE INTO classes (term, course_number, section, course_title, room, meeting_pattern, enrollment, max_enrollment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (entry['Term'], entry['Course'], entry['Section #'], entry['Course Title'], entry['Room'], entry['Meeting Pattern'], 
                    int(entry['Enrollment']), int(entry['Maximum Enrollment'])))
            # Get the newest class ID
            class_id = cursor.lastrowid

            # Parse intstructor from csv and get needed info for adding to database
            results = parse_instructor(entry['Instructor'])
            
            for professor_dict in results:
                first_name = professor_dict['first_name']
                last_name = professor_dict['last_name']
                professor_id = professor_dict['p_id']

                # Insert the class-professor relationship into the class_professors table and 
                # add the professor to the database if they don't exist
                get_or_create_professor(cursor, first_name, last_name, professor_id, class_id)
                
    conn.commit()
    conn.close()

    print("Data should now properly be inserted into the database from the csv file")

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
    relevant_columns = ["Term", "Course", "Section #", "Course Title", "Room", 
                        "Meeting Pattern", "Enrollment", "Maximum Enrollment", 
                        "Cross-listings", "Instructor", "Cross-list Maximum"]

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
                    "Maximum Enrollment": int(row[col_indexes["Maximum Enrollment"]]),
                    "Cross-listings": row[col_indexes["Cross-listings"]].strip(),
                    "Instructor": row[col_indexes["Instructor"]].strip(),
                    "Cross-list Maximum": int(row[col_indexes["Cross-list Maximum"]]) if row[col_indexes["Cross-list Maximum"]].strip() else 0

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


# API Route to swap (relevant) class data
@app.route("/class/<int:class_id>/swap/<int:swap_id>", methods=["POST"])
def swap_classes(class_id, swap_id):
    """
    Swaps two classes' data.
    
    Both classes have to reside in the database.

    :return: JSON response indicating success or an error message.
    :rtype: flask.Response

    :status 200: Successfully swapped classes
    :status 400: Failed to swap classes
    :status 404: One of the classes was not found
    """
    # Get current class details
    c1 = get_class_details(class_id)
    c2 = get_class_details(swap_id)

    if c1 and c2:
        # Only the max enrollment and room location need to be swapped
        temp = [c2["maxEnrollment"], c2["room"]]
        c2["maxEnrollment"] = c1["maxEnrollment"]
        c2["room"] = c1["room"]
        c1["maxEnrollment"] = temp[0]
        c1["room"] = temp[1]

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('UPDATE classes SET max_enrollment = ?, room = ? WHERE id = ?', (c1["maxEnrollment"], c1["room"], c1["id"]))
            cursor.execute('UPDATE classes SET max_enrollment = ?, room = ? WHERE id = ?', (c2["maxEnrollment"], c2["room"], c2["id"]))
            conn.commit()
            return jsonify('Successfully swapped classes.', 200)
        except Exception:
            return jsonify('Failed to insert changes into the database.', 400)
        finally:
            conn.close()
    else:
        # realistically this shouldn't hit
        return jsonify('Could not find one of the classes.', 404)


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
                        cursor.execute("SELECT enrollment FROM classes WHERE id = ?", (id,))
                        new_enrollment_count = cursor.fetchall()[0][0]
                        data[0] = None # so it doesn't get quoted in the csv file
                        data[28] = new_enrollment_count # 28 is the index of the current enrollment count. if there's a more dynamic way to do this in case the data format changes, let's do that instead

                        writer.writerow(data)
                        id += 1
                else: # copy row
                    with open("output.csv", "a", newline='', encoding="utf-8") as out_file:
                        writer = csv.writer(out_file, quoting=csv.QUOTE_NOTNULL)
                        writer.writerow(row)

    except Exception:
        return jsonify("No database exists."), 404
    finally:
        conn.close()
    print("Successfully exported data to file.")
    return jsonify('Successfully exported data to file.'), 200


# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
