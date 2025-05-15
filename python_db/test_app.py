import io
import os
import tempfile
import pytest
import csv
import sqlite3
from app import app

@pytest.fixture(autouse=True)
def setup_database():
    # Create the classes table if it doesn't exist
    conn = sqlite3.connect(app.config["DB_FILE"])
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()
    
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Classes page confirmation
def test_get_classes(client):
    response = client.get('/classes')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

# Testing a successful import
def test_upload_success(client, mocker):
    # Realistic CSV content for a couple columns of our database
    csv_content = b"""Term,Course,Section #,Course Title,Room,Meeting Pattern,Enrollment,Maximum Enrollment,Cross-listings,Instructor,Cross-list Maximum
Fall 2025,CSCI1010,001,Intro to CS,PKI 160,TTh 9:00-10:15,28,30,,Dr. Smith,
Fall 2025,CSCI1020,002,Data Structures,PKI 170,MW 10:30-11:45,32,30,CSCI1030,Dr. Doe,50
"""

    data = {
        'file': (io.BytesIO(csv_content), 'test.csv')
    }

    # Mock downstream dependencies
    mocker.patch('app.fix_csv', return_value='uploads/test.csv')
    mocker.patch('app.create_tables')
    mocker.patch('app.parse_csv', return_value=[
        {
            "Term": "Fall 2025",
            "Course": "CSCI1010",
            "Section #": "001",
            "Course Title": "Intro to CS",
            "Room": "PKI 160",
            "Meeting Pattern": "TTh 9:00-10:15",
            "Enrollment": "28",
            "Maximum Enrollment": "30",
            "Cross-listings": "",
            "Instructor": "Dr. Smith",
            "Cross-list Maximum": ""
        },
        {
            "Term": "Fall 2025",
            "Course": "CSCI1020",
            "Section #": "002",
            "Course Title": "Data Structures",
            "Room": "PKI 170",
            "Meeting Pattern": "MW 10:30-11:45",
            "Enrollment": "32",
            "Maximum Enrollment": "30",
            "Cross-listings": "CSCI1030",
            "Instructor": "Dr. Doe",
            "Cross-list Maximum": "50"
        }
    ])
    mocker.patch('app.insert_csv_into_table')

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    assert response.status_code == 200
    json_data = response.get_json()
    print(json_data)
    assert "message" in json_data and json_data["message"] == "File uploaded successfully!"
    assert "file_path" in json_data

# Testing import for errors
def test_upload_processing_error(client, mocker):
    csv_content = b"""Term,Course,Section #,Course Title,Room,Meeting Pattern,Enrollment,Maximum Enrollment,Cross-listings,Instructor,Cross-list Maximum
Fall 2025,CSCI9999,999,Fake Course,Nowhere,None,0,0,,None,
"""
    data = {
        'file': (io.BytesIO(csv_content), 'bad.csv')
    }

    mocker.patch('app.fix_csv', return_value='uploads/bad.csv')
    mocker.patch('app.create_tables')
    mocker.patch('app.parse_csv', side_effect=ValueError("Simulated parse failure"))

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    print(response)

    assert response.status_code == 400
    assert "Simulated parse failure" in response.get_json()["error"]

# def test_export_success(client, tmp_path):
#     csv_content = b"""Fall 2025
# Generated Placeholder
# ,Term,Course,Section #,Course Title,Room,Meeting Pattern,Enrollment,Maximum Enrollment,Cross-listings,Instructor,Cross-list Maximum
# ,Fall 2025,CSCI1010,001,Intro to CS,PKI 160,TTh 9:00-10:15,28,30,,Dr. Smith,
# """

#     # mock an input csv file
#     mock_input_path = tmp_path / "mock_input.csv"
#     mock_input_path.write_bytes(csv_content)

#     # Patch the global file_path inside app
#     app.file_path = str(mock_input_path)

#     desktop_dir = tmp_path / "Desktop"
#     desktop_dir.mkdir()
#     os.environ["USERPROFILE"] = str(tmp_path)

#     # create mock database
#     db_path = tmp_path / "test.db"
#     app.config["DB_FILE"] = str(db_path)
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()

#     cursor.execute('''
#         CREATE TABLE classes (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             term TEXT,
#             course TEXT,
#             section TEXT,
#             course_title TEXT,
#             room TEXT,
#             meeting_pattern TEXT,
#             enrollment INTEGER
#         )
#     ''')
#     cursor.execute("INSERT INTO classes (term, course, section, course_title, room, meeting_pattern, enrollment) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                    ("Fall 2025", "CSCI1010", "001", "Intro to CS", "PKI 160", "TTh 9:00-10:15", 35))
#     conn.commit()
#     conn.close()

#     # get a response from the export path
#     response = client.put("/export")
#     assert response.status_code == 200
#     assert "Successfully exported" in response.get_json()

#     # check that an output file was created
#     output_file = desktop_dir / "output.csv"
#     assert output_file.exists()

#     with open(output_file, newline='', encoding="utf-8") as f:
#         reader = list(csv.reader(f))
#         assert reader[0][0] == "Fall 2025"
#         assert "Generated" in reader[1][0]
#         assert reader[3][7] == "35"


def test_swap_classes_success(client, tmp_path):
    
    db_path = tmp_path / "test.db"
    app.config["DB_FILE"] = str(db_path)
    
    # Create test database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT,
        courseName TEXT,
        section TEXT,
        course_title TEXT,
        room TEXT,
        meeting_pattern TEXT,
        enrollment INTEGER,
        max_enrollment INTEGER
    )
""")
    # Insert two classes
    cursor.execute("""
    INSERT INTO classes (term, courseName, section, course_title, room, meeting_pattern, enrollment, max_enrollment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", ("Fall 2025", "CSCI1010", "001", "Intro to CS", "PKI 160", "TTh 9:00-10:15", 28, 30))

    cursor.execute("""
    INSERT INTO classes (term, courseName, section, course_title, room, meeting_pattern, enrollment, max_enrollment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", ("Fall 2025", "CSCI1020", "002", "Data Structures", "PKI 170", "MW 10:30-11:45", 32, 40))
    conn.commit()
    class1_id = cursor.execute("SELECT id FROM classes WHERE courseName = 'CSCI1010'").fetchone()[0]
    class2_id = cursor.execute("SELECT id FROM classes WHERE courseName = 'CSCI1020'").fetchone()[0]
    conn.close()

    payload = {
        "crowded_id": class1_id,
        "target_id": class2_id,
        "different_timeslot": False  
    }

    response = client.post("/swap-classrooms", json=payload)
    assert response.status_code == 200 or response.get_json() == "Successfully swapped classes."

    # check the database to verify values were swapped
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    updated1 = cursor.execute("SELECT max_enrollment, room FROM classes WHERE id = ?", (class1_id,)).fetchone()
    updated2 = cursor.execute("SELECT max_enrollment, room FROM classes WHERE id = ?", (class2_id,)).fetchone()
    print(updated1)
    print(updated2)
    conn.close()

    assert updated1 == (40, "PKI 170")  # c1 now has c2's values
    assert updated2 == (30, "PKI 160")  # c2 now has c1's values

def test_swap_recommendations_sameslot(client, tmp_path):

    db_path = tmp_path / "test.db"
    app.config["DB_FILE"] = str(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create necessary tables
    cursor.execute('''
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            course TEXT,
            section TEXT,
            course_title TEXT,
            room TEXT,
            meeting_pattern TEXT,
            enrollment INTEGER,
            max_enrollment INTEGER,
            instructor TEXT,
            course_number TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE class_professors (
            class_id INTEGER,
            professor_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    # Insert test data
    cursor.executemany('INSERT INTO professors (name) VALUES (?)', [("Dr. A",), ("Dr. B",), ("Dr. C",)])

    test_classes = [
        ("Fall 2025", "CSCI1010", "001", "Intro to CS", "PKI 160", "TTh 9:00-10:15", 35, 30, "Dr. A", "CSCI1010"),
        ("Fall 2025", "CSCI1020", "001", "Data Structures", "PKI 170", "TTh 9:00-10:15", 15, 40, "Dr. B", "CSCI1020"),
        ("Fall 2025", "CSCI1030", "001", "Algorithms", "PKI 180", "MW 11:30-12:45", 25, 30, "Dr. C", "CSCI1030"),
    ]
    cursor.executemany('''
        INSERT INTO classes (term, course, section, course_title, room, meeting_pattern, enrollment, max_enrollment, instructor, course_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_classes)

    # Link professors to classes 
    cursor.executemany('INSERT INTO class_professors (class_id, professor_id) VALUES (?, ?)', [(1, 1), (2, 2), (3, 3)])

    conn.commit()
    conn.close()

    response = client.get("/swap-recommendations")
    assert response.status_code == 200

    data = response.get_json()
    print(data)
    assert "same_slot_swaps" in data
    assert "cross_slot_recommendations" in data
    
def test_swap_recommendations_differentslot(client, tmp_path):

    db_path = tmp_path / "test.db"
    app.config["DB_FILE"] = str(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create necessary tables
    cursor.execute('''
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            course TEXT,
            section TEXT,
            course_title TEXT,
            room TEXT,
            meeting_pattern TEXT,
            enrollment INTEGER,
            max_enrollment INTEGER,
            instructor TEXT,
            course_number TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE class_professors (
            class_id INTEGER,
            professor_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    # Insert test data
    cursor.executemany('INSERT INTO professors (name) VALUES (?)', [("Dr. A",), ("Dr. B",), ("Dr. C",)])

    test_classes = [
        ("Fall 2025", "CSCI1010", "001", "Intro to CS", "PKI 160", "TTh 9:00-10:15", 35, 30, "Dr. A", "CSCI1010"),
        ("Fall 2025", "CSCI1020", "001", "Data Structures", "PKI 170", "MW 9:00-10:15", 15, 40, "Dr. B", "CSCI1020"),
        ("Fall 2025", "CSCI1030", "001", "Algorithms", "PKI 180", "MW 11:30-12:45", 25, 30, "Dr. C", "CSCI1030"),
    ]
    cursor.executemany('''
        INSERT INTO classes (term, course, section, course_title, room, meeting_pattern, enrollment, max_enrollment, instructor, course_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', test_classes)

    # Link professors to classes 
    cursor.executemany('INSERT INTO class_professors (class_id, professor_id) VALUES (?, ?)', [(1, 1), (2, 2), (3, 3)])

    conn.commit()
    conn.close()

    response = client.get("/swap-recommendations")
    assert response.status_code == 200

    data = response.get_json()
    print(data)
    assert "same_slot_swaps" in data
    assert "cross_slot_recommendations" in data


def test_swap_recommendations_no_classes(client, tmp_path):
    db_path = tmp_path / "test.db"
    app.config["DB_FILE"] = str(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create necessary tables, but don't insert any data
    cursor.execute('''
        CREATE TABLE classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT,
            course TEXT,
            section TEXT,
            course_title TEXT,
            room TEXT,
            meeting_pattern TEXT,
            enrollment INTEGER,
            max_enrollment INTEGER,
            instructor TEXT,
            course_number TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE class_professors (
            class_id INTEGER,
            professor_id INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE professors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    conn.commit()
    conn.close()

    # Make the GET request with an empty DB
    response = client.get("/swap-recommendations")
    assert response.status_code == 200

    data = response.get_json()
    print(data)
    assert data["same_slot_swaps"] == {}
    assert data["cross_slot_recommendations"] == {}