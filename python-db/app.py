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

# API Route to fetch class details by ID 
@app.route("/class/<int:class_id>", methods=["GET"])
def get_class(class_id):
    conn = sqlite3.connect(DB_FILE)  # Connect to database
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id))
    # fetch just one row as theres only one class per id
    row = cursor.fetchone()
    conn.close()

    if row:
        class_data = {
            "id": row[0],
            "term": row[1],
            "section": row[2],
            "name": row[3],  # Course Title
            "room": row[4],
            "time": row[5],
            "currentEnrollment": row[6],
            "maxEnrollment": row[7]
        }
        # serialize and return class data if class is found
        return jsonify(class_data), 200
    else:
        # otherwise provide a 404 error and message along with it 
        return jsonify({"message": "Class not found"}), 404
    
# Start the Flask Server
if __name__ == "__main__":
    app.run(debug=True)
