import io
import pytest
import sqlite3
from app import app, DB_FILE

@pytest.fixture(autouse=True)
def setup_database():
    # Create the classes table if it doesn't exist
    conn = sqlite3.connect(DB_FILE)
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