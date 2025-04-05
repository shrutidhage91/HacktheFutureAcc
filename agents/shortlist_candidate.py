import sqlite3

def shortlist_candidates(job_title: str, min_match_score: float):
    """Fetch candidates who meet the job title criteria and have a match score above the threshold."""

    # Connect to the SQLite database
    conn = sqlite3.connect("job_screening.db")  # Update with your actual DB name
    cursor = conn.cursor()

    # Query to join candidate_data with match_scores on email
    query = """
    SELECT c.candidate_name, c.email, c.phone_number, c.job_title, 
           c.skills, c.experience, c.education, m.match_score
    FROM candidate_data c
    JOIN match_scores m ON c.email = m.email
    WHERE c.job_title = ? AND m.match_score >= ?
    ORDER BY m.match_score DESC
    """

    cursor.execute(query, (job_title, min_match_score))
    shortlisted_candidates = cursor.fetchall()

    # Close DB connection
    conn.close()

    # Format results
    result = []
    for candidate in shortlisted_candidates:
        result.append({
            "candidate_name": candidate[0],
            "email": candidate[1],
            "phone_number": candidate[2],
            "job_title": candidate[3],
            "skills": candidate[4],
            "experience": candidate[5],
            "education": candidate[6],
            "match_score": candidate[7],
        })

    return result  # Returns a list of shortlisted candidates

# Example Usage:
if __name__ == "__main__":
    job_title = "Data Scientist"
    min_match_score = 0.80
    shortlisted = shortlist_candidates(job_title, min_match_score)
    
    for candidate in shortlisted:
        print(candidate)
