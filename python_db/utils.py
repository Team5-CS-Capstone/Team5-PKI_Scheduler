# This file is used for utility functions that are used in the app.py file.
# It contains mostly functions to parse / regularize data from the csv file and insert it into the database.

import re

def parse_instructor(instructor_from_csv):
    """
    Parse instructor data from the csv file and return information
    to insert into the professors database table.
    """
    # Split the instructor string into first and last names
    # Pattern explained:
    #  1) ([^,]+) -> captures last name up to the comma
    #  2) ,\s* -> matches the comma and any space
    #  3) ([^(]+) -> captures first name(s) up to '('
    #  4) \((\d+)\) -> captures the numeric ID in parentheses
    #  5) \[([^\]]+)\] -> captures the roles (whatever is inside [])
    pattern = re.compile(r"([^,]+),\s*([^(]+)\((\d+)\)\s*\[([^\]]+)\]")
    
    # Split on semicolons in case there are multiple instructors
    instructor_chunks = [i.strip() for i in instructor_from_csv.split(';')]

    results = []
    for chunk in instructor_chunks:
        match = pattern.search(chunk)
        if match:
            last_name = match.group(1).strip()
            first_name = match.group(2).strip()
            p_id = match.group(3).strip()

            results.append({
                "first_name": first_name,
                "last_name": last_name,
                "p_id": p_id,
                "email": match.group(4).strip()
            })

    return results

def get_or_create_professor(cursor, first_name, last_name, p_id):
    """
    Get or create a professor in the database.
    This function will check if the professor already exists in the database
    and if not, it will create a new entry.
    """
    cursor.execute("SELECT * FROM professors WHERE first_name = ? AND last_name = ? and p_id = ?", (first_name, last_name, p_id))
    professor = cursor.fetchone()

    if professor:
        # Professor already exists, return the existing entry
        return professor[0]
    else:
        cursor.execute("INSERT INTO professors(first_name, last_name, p_id) VALUES(?, ?, ?)",
                    (first_name, last_name, p_id))
        return cursor.lastrowid
