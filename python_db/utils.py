# This file is used for utility functions that are used in the app.py file.
# It contains mostly functions to parse / regularize data from the csv file and insert it into the database.

import re, csv

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

def get_or_create_professor(cursor, first_name, last_name, p_id, class_id):
    """
    Get or create a professor in the database.
    This function will check if the professor already exists in the database
    and if not, it will create a new entry.
    """
    cursor.execute("SELECT * FROM professors WHERE first_name = ? AND last_name = ? and p_id = ?", (first_name, last_name, p_id))
    professor = cursor.fetchone()

    if professor:
        # Professor already exists, return the existing entry
        # use this id to insert into the class_professors table
        professor_id = professor[0]
    else:
        # Professor does not exist, insert a new entry
        # and get this id to insert into the class_professors table
        cursor.execute("INSERT OR IGNORE INTO professors(first_name, last_name, p_id) VALUES(?, ?, ?)",
                    (first_name, last_name, p_id))
        professor_id = cursor.lastrowid    

    # Insert the class-professor relationship into the class_professors table
    # if the professor already exists
    cursor.execute("""INSERT OR IGNORE INTO class_professors (class_id, professor_id)
                            VALUES (?, ?)""", (class_id, professor_id)) 

    
'''Function to fix the trailing commas in the csv'''
def fix_csv(csv_document):
    '''Cannot open the same file for input and output to write, take the extension and and -fix to it to have two separate files'''
    fixed_csv = csv_document.replace(".csv", "-fix.csv")
    '''Open the csv doc and the output file temporarily created'''
    with open(csv_document, 'r', newline='') as csv_to_clean, open(fixed_csv, 'w', newline='') as output_csv:
        reader = csv.reader(csv_to_clean)
        writer = csv.writer(output_csv)
        '''Loop to check if the last part of the row is empty and delete appropriately'''
        for row in reader:
            while row and row[-1] == '':
                row.pop()
            writer.writerow(row)
        '''Return fixed sheet'''
    return fixed_csv
    
