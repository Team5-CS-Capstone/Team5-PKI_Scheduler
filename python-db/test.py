import sqlite3
import sys
import os
import csv
DB_FILE = "database1 .db"
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
            term TEXT,
            course_number TEXT,
            section TEXT,
            course_title TEXT,
            room TEXT,
            meeting_pattern TEXT,
            enrollment INTEGER,
            max_enrollment INTEGER,
            PRIMARY KEY (term, course_number, section)
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

    cross_lists = {}
    for entry in course_data:
        cross_list = entry.get("Cross-listings", "").strip()
        if cross_list:
            courses = [course_num.strip() for course_num in cross_list.split('/')]
            cross_list_key = " / ".join(sorted(courses))
            if cross_list_key not in cross_lists:
                cross_lists[cross_list_key] = []
            cross_lists[cross_list_key].append(entry["Course"])
    print(cross_lists)
    # for entry in course_data:
    for entry in course_data:
        course = entry["Course"]
        cross_list = entry.get("Cross-listings", "").strip()
        if cross_list:
            courses = [course_num.strip() for course_num in cross_list.split('/')]
            cross_list_key = " / ".join(sorted(courses))
        if cross_list_key in cross_list and course in cross_lists[cross_list_key]:
            group_crosslists = []
            for cross_list_entry in course_data:
                if cross_list_entry["Course"] in cross_lists[cross_list_key]:
                    group_crosslists.append(cross_list_entry)
            total_enrollment = sum(int(e["Enrollment"]) for e in group_crosslists)
            total_max = sum(int(e["Maximum Enrollment"]) for e in group_crosslists)
            grouped_class = group_crosslists[0]

            cursor.execute("""INSERT OR IGNORE INTO classes (term, course_number, section, course_title, room, meeting_pattern, enrollment, max_enrollment) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
             """, (grouped_class['Term'], cross_list_key, grouped_class['Section #'], grouped_class['Course Title'], grouped_class['Room'], grouped_class['Meeting Pattern'], total_enrollment, total_max))
        else:
            cursor.execute("""
                INSERT OR IGNORE INTO classes (term, course_number, section, course_title, room, meeting_pattern, enrollment, max_enrollment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (entry['Term'], entry['Course'], entry['Section #'], entry['Course Title'], entry['Room'], entry['Meeting Pattern'], 
                    int(entry['Enrollment']), int(entry['Maximum Enrollment'])))

    conn.commit()
    conn.close()




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
    relevant_columns = ["Term", "Course", "Section #", "Course Title", "Room", "Meeting Pattern", "Enrollment", "Maximum Enrollment", "Cross-listings"]

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
                    "Cross-listings": row[col_indexes["Cross-listings"]].strip()
                })
    
    # Returns a list of dicts (one dict per class entry)
    return course_data

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, "../../"))  # Adjust if needed
data_dir = os.path.join(repo_root, "Team5-PKI_Scheduler\\python-db\\")
input_file = os.path.join(data_dir, "cleaned.csv")
a = parse_csv(input_file)
create_tables()
insert_csv_into_table(a)
print(a)
