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

    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200

    
# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
