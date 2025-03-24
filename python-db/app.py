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
# Allow frontend requests using CORS
CORS(app)  

# Our SQLite database file
DB_FILE = "database.db"

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
    
@app.route("/export")
def export_to_csv():
    conn = sqlite3.connect(DB_FILE)
    # check to make sure the connection worked
    # likely will remove this later. I'm thinking we disable the button if theres no database/problems if possible
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM classes")

        # CHANGE THIS WHEN THE IMPORT BUTTON WORKS - COPIED FROM import_csv_to_table.py
        # currently I'm relying on the input csv file to read all the excess data from to make a perfect copy of the file, with the changes that were made
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Adjust if needed
        data_dir = os.path.join(repo_root, "Team5-PKI_Scheduler\\my-vue-app\\")
        input_file = os.path.join(data_dir, "Spring2023.csv")

        # the idea here is to go line by line
        # copy each line into a list. if there's something in the first list, process depending on where it is (date, class name, etc.)
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
            id = 1
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

        print("done writing :)")

        # # clear the output csv file
        # # overwrite the csv file with new data? create a new file with just the data from the database, then merge the two?
        # with open("output.csv", "w", newline = '', encoding="utf-8") as out_file:
        #     writer = csv.writer(out_file)
        #     # out_file.write("\"Fall 2025\"\n\"Generated DATE, TIME\"\n,")
        #     # writer.writerow(headers)
        #     for row in cursor.fetchall():
        #         writer.writerow(row[1:]) # Don't need ID

        # READ THROUGH THE INPUT. GO LINE BY LINE. IF AFTER READING A LINE THERES SOMETHING IN THE FIRST CELL, DO SOMETHING (just print?) OTHERWISE PROCESS
    except Exception:
        return jsonify("No database exists :("), 404
    finally:
        conn.close()
    return jsonify('Successfully exported data to file'), 200
    
# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
