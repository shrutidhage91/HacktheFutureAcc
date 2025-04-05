import sqlite3
import json
import subprocess

DB_FILE = 'job_screening.db'

def create_tables():
    """
    Creates the job_descriptions table if it doesn't already exist.
    The table stores the original job description text and its JSON summary.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""DROP TABLE IF EXISTS job_descriptions""")
    cursor.execute('''
        CREATE  table job_descriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT,
            required_skills TEXT,
            experience TEXT,
            qualification TEXT,
            responsibilities TEXT
        )
    ''')

    #conn.execute("""drop table if exists candidate_data""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS candidate_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


    conn.commit()
    conn.close()
create_tables()