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