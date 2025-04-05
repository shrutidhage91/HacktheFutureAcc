import sqlite3
import ollama
import numpy as np

# Define job title for matching
job_title = "Data Scientist"

def get_job_description(job_title):
    """Fetches job description from job_description table for a given job title."""
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT job_title,required_skills,experience,qualifications,responsibilities FROM job_descriptions WHERE job_title = ?", (job_title,))
    jd_row = cursor.fetchone()
    
    conn.close()
    
    if not jd_row:
        print(f"No job description found for '{job_title}'")
        return None

    # Convert to dictionary
    jd_summary = {
        "job_title": jd_row[0],
        "required_skills": jd_row[1].split(", "),
        "experience": jd_row[2],
        "qualifications": {"education": jd_row[3]},
        "responsibilities": jd_row[4].split(", ")
    }
    
    return jd_summary

def get_candidate_data(job_title):
    """Fetches all candidates from candidate_data table."""
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT candidate_name,email,job_title,education, experience,skills,certification FROM candidate_data_norm where job_title= ?",(job_title,))
    candidates = cursor.fetchall()
    
    conn.close()

    if not candidates:
        print("No candidates found in the database.")
        return []

    candidate_list = []
    for row in candidates:
        candidate = {
            "candidate_name": row[0],
            "email":row[1],
            "job_title": row[2],
            "skills": row[5].split(", ") if row[5] else [],
            "experience": row[4].split(", ") if row[4] else [],
            "education": row[3],
        }
        candidate_list.append(candidate)

    return candidate_list

def compute_match(candidate, jd_summary):
    """Computes similarity score using Ollama's embedding model."""
    candidate_text = (
        candidate.get("job_title", "") + " " +
        ", ".join(candidate.get("skills", [])) + " " +
        ", ".join(candidate.get("experience", [])) + " " +
        candidate.get("education", "")
    )

    jd_text = (
        jd_summary.get("job_title", "") + " " +
        ", ".join(jd_summary.get("required_skills", [])) + " " +
        ", ".join(jd_summary.get("responsibilities", [])) + " " +
        jd_summary.get("qualifications", {}).get("education", "")
    )

    # Get embeddings from Ollama
    candidate_embedding = ollama.embeddings(model="mxbai-embed-large", prompt=candidate_text)["embedding"]
    jd_embedding = ollama.embeddings(model="mxbai-embed-large", prompt=jd_text)["embedding"]

    # Convert to NumPy arrays
    candidate_embedding = np.array(candidate_embedding)
    jd_embedding = np.array(jd_embedding)

    # Compute cosine similarity
    similarity_score = np.dot(candidate_embedding, jd_embedding) / (
        np.linalg.norm(candidate_embedding) * np.linalg.norm(jd_embedding)
    )

    return round(float(similarity_score), 3)
def save_match_scores(match_results):
    """Saves computed match scores to match_scores table."""
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_scores (
            candidate_name TEXT,
            email TEXT,
            job_title TEXT,
            match_score REAL
        )
    """)

    # Insert match scores
    for result in match_results:
        cursor.execute("""
            INSERT INTO match_scores (candidate_name, email, job_title, match_score)
            VALUES (?, ?, ?, ?)
        """, (result["candidate_name"], result["email"], result["job_title"], result["match_score"]))

    conn.commit()
    conn.close()
    print("Match scores saved successfully.")

def main():
    """Main function to run the match scoring process."""
    conn = sqlite3.connect("job_screening.db")
    cur = conn.cursor()
    job_titles = cur.execute("""select distinct job_title from job_descriptions""")
    job_titles = [title[0] for title in job_titles]
    print(job_titles)
    # Step 1: Fetch job description
    for job_title in job_titles:
        jd_summary = get_job_description(job_title)
        print(jd_summary)
        if not jd_summary:
            return "No job description found for the given job_title"
        
        # Step 2: Fetch candidate data
        candidates = get_candidate_data(job_title)
        print("candidates",candidates)
        if not candidates:
            return "No candidate found for the given job_title"
        
        match_results = []
        for candidate in candidates:
            score = compute_match(candidate, jd_summary)
            match_results.append({
                "candidate_name": candidate["candidate_name"],
                "email": candidate["email"],
                "job_title": candidate["job_title"],
                "match_score": score
            })
            print(match_results)
        
        # Step 4: Save match scores to database
        save_match_scores(match_results)

        # Print match results
        for result in match_results:
            print(f"Candidate: {result['candidate_name']}, Score: {result['match_score']}")

if __name__ == "__main__":
    main()
