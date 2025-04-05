import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from agents.interview_scheduler import *

def get_job_titles():
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT job_title FROM job_descriptions")
    jobs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jobs

def get_job_details(job_title):
    conn = sqlite3.connect("job_screening.db")
    query = "SELECT * FROM job_descriptions WHERE job_title = ?"
    df = pd.read_sql_query(query, conn, params=(job_title,))
    conn.close()
    return df

def get_shortlisted_candidates(job_title, min_score):
    conn = sqlite3.connect("job_screening.db")
    query = """
        SELECT distinct c.candidate_name, c.job_title,c.email,c.phone_number,c.education,c.projects,c.experience,c.skills,c.certification, m.match_score FROM candidate_data c
        JOIN match_scores m ON c.email = m.email
        WHERE m.job_title = ? AND m.match_score >= ?
    """
    df = pd.read_sql_query(query, conn, params=(job_title, min_score))
    conn.close()
    return df

def generate_email_preview(candidate_name, job_title, recruiter_name, recruiter_email):
    interview_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    email_preview = f"""
    Subject: Interview Invitation for {job_title} Role

    Dear {candidate_name},

    We are pleased to invite you for an interview for the {job_title} position.
    
    Proposed Date & Time: {interview_date}
    
    Please confirm your availability.
    
    Best Regards,
    {recruiter_name}
    {recruiter_email}
    """
    return email_preview

# Streamlit UI
st.title("Recruiter Dashboard")

# Job Selection
st.sidebar.header("Select Job Title")
jobs = get_job_titles()
selected_job = st.sidebar.selectbox("Choose a job title", jobs)

if selected_job:
    st.subheader(f"Job Description: {selected_job}")
    job_details = get_job_details(selected_job)
    st.write(job_details)

    # Shortlisting candidates
    st.subheader("Shortlisted Candidates")
    min_match_score = st.slider("Minimum Match Score", 0.0, 1.0, 0.7)
    shortlisted_df = get_shortlisted_candidates(selected_job, min_match_score)
    display_df=shortlisted_df.drop(columns=['email','phone_number'],errors='ignore')
    st.write(display_df)

    # Interview Scheduling Preview
    if not shortlisted_df.empty:
        candidate_name = shortlisted_df.iloc[0]['candidate_name']
        candidate_email = shortlisted_df.iloc[0]['email']
        recruiter_name = "Recruiter Name"  # Replace with actual recruiter info
        recruiter_email = "recruiter@example.com"
        recruiter_phone = "+1-123-456-7890"
        st.subheader("Email Preview")
        #email_content = generate_email_preview(candidate_name, selected_job, recruiter_name, recruiter_email)
        email_content = generate_email_preview(candidate_name, selected_job, recruiter_name, recruiter_email)
        #email_content = schedule_interviews(shortlisted_df, recruiter_email, recruiter_phone)
        st.text_area("Interview Email", email_content, height=200)
    else:
        st.write("No shortlisted candidates meet the criteria.")
