import sqlite3
import json


# Sample data: list of dictionaries representing job rows
rows = [
    {
        'required_skills': ['Python', 'Java', 'C++', 'Database Proficiency', 'Web Development', 'Software Frameworks'],
        'experience': 'Not specified, but experience with databases, web development, and software frameworks is required.',
        'qualifications': {
            'education': "Bachelor's degree in Computer Science or a related field.",
            'soft_skills': ['Strong problem-solving skills', 'Attention to detail', 'Ability to work both independently and in a team environment']
        },
        'responsibilities': [
            'Develop, test, and deploy software applications.',
            'Write clean, maintainable, and scalable code.',
            'Collaborate with cross-functional teams to define and implement features.',
            'Troubleshoot and debug issues for optimal performance.',
            'Stay updated with emerging technologies and best practices.'
        ],
        'job_title': 'Software Engineer'
    },
    {
        'required_skills': ['Python', 'R', 'SQL', 'Machine Learning Frameworks', 'Data Visualization Tools (e.g., Tableau, Power BI)'],
        'experience': 'Not specified in the job description, but it is implied that there should be experience in data science and machine learning.',
        'qualifications': ["Bachelor's or Master's degree in Data Science, Computer Science, or a related field."],
        'responsibilities': [
            'Collect, clean, and analyze large datasets.',
            'Develop and deploy machine learning models.',
            'Build predictive analytics solutions to improve business outcomes.',
            'Communicate findings through reports and visualizations.',
            'Stay updated with advancements in data science and AI.'
        ],
        'job_title': 'Data Scientist'
    }
]

DB_FILE = "job_screening.db"

def create_connection(db_file: str = DB_FILE) -> sqlite3.Connection:
    """Create a database connection to the SQLite database specified by db_file."""
    conn = sqlite3.connect(db_file)
    return conn

def create_table(conn: sqlite3.Connection):
    """
    Creates the job_descriptions table if it doesn't already exist.
    The table includes columns for job_title, required_skills, experience,
    qualifications, and responsibilities.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        required_skills TEXT,
        experience TEXT,
        qualifications TEXT,
        responsibilities TEXT
    );
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS job_descriptions""")
        cursor.execute(create_table_sql)
        conn.commit()
    except sqlite3.Error as e:
        print("Error creating table:", e)

def insert_job_data(conn: sqlite3.Connection, jobs: list):
    """
    Inserts a list of job dictionaries into the job_descriptions table.
    Converts list/dict fields into JSON strings before inserting.
    """
    sql = """
    INSERT INTO job_descriptions (job_title, required_skills, experience, qualifications, responsibilities)
    VALUES (?, ?, ?, ?, ?)
    """
    
    # Prepare data by converting fields to JSON where appropriate.
    data_to_insert = []
    print(jobs)
    for job in jobs:
        job_title = job.get("job_title", "")
        # Convert lists and dictionaries to JSON strings for storage.
        required_skills = json.dumps(job.get("required_skills", []))
        experience = job.get("experience", "")
        qualifications = json.dumps(job.get("qualifications", {}))
        responsibilities = json.dumps(job.get("responsibilities", []))
        
        data_to_insert.append((job_title, required_skills, experience, qualifications, responsibilities))
    
    try:
        cur = conn.cursor()
        cur.executemany(sql, data_to_insert)
        rows=cur.execute("""select * from job_descriptions""")
        for row in rows:
            print(row)
        conn.commit()
        print(f"Inserted {cur.rowcount} rows into the job_descriptions table.")
    except sqlite3.Error as e:
        print("Error inserting data:", e)

if __name__ == "__main__":
    # Create a connection and ensure table exists
    connection = create_connection()
    create_table(connection)
    
    # Insert the job rows into the database
    insert_job_data(connection, rows)
    
    # Close the connection
    connection.close()
