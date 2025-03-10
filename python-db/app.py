from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os

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
    
        # overwrite the csv file with new data
        with open("output.txt", "w", encoding="utf-8") as out_file:
            out_file.write("test")

        print("Done writing data")
    except Exception:
        return jsonify("No database exists :(")
    return jsonify('Successfully exported data to file'), 200
    
# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
