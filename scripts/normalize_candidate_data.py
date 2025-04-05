import sqlite3

def normalize_job_titles():
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS candidate_data_norm (
            candidate_name TEXT,
            email TEXT,
            phone_number TEXT,
            job_title TEXT,
            education TEXT,
            projects TEXT,
            experience TEXT,
            skills TEXT,
            certification TEXT
            
        )
    """)

    # Step 1: Fetch all rows from candidate_data
    cursor.execute("SELECT candidate_name,email,phone_number,job_title,education,projects,experience,skills,certification FROM candidate_data")
    rows = cursor.fetchall()

    # Step 2: Get column names (important for re-inserting)
    col_names = [description[0] for description in cursor.description]

    # Step 4: Re-insert normalized data
    for row in rows:
        data = dict(zip(col_names, row))
        job_titles = [title.strip() for title in data["job_title"].split(",")]

        for jt in job_titles:
            data["job_title"] = jt
            values = [data[col] for col in col_names]
            placeholders = ', '.join(['?'] * len(values))
            cursor.execute(f"INSERT INTO candidate_data_norm ({', '.join(col_names)}) VALUES ({placeholders})", values)

    conn.commit()
    conn.close()
    print("Job titles normalized successfully.")

normalize_job_titles()

