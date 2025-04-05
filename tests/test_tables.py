import sqlite3

conn = sqlite3.connect("job_screening.db")
cur = conn.cursor()
cur.execute("""select distinct job_title from candidate_data_norm""")
print(cur.fetchall()) 
cur.execute("""select distinct job_title from job_descriptions""")
print(cur.fetchall()) 
#print(cur.fetchone())
#print(cur.fetchmany(3))               