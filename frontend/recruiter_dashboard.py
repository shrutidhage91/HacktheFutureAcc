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
        SELECT DISTINCT c.candidate_name, c.job_title, c.email, c.phone_number,
           c.education AS education,
           c.skills AS skills,
           c.projects AS projects,
           c.experience AS experience,
           c.certification AS certification,
           MAX(m.match_score) AS match_score
    FROM candidate_data_norm c
    JOIN match_scores m ON c.email = m.email
    WHERE m.job_title = ? 
      AND m.match_score >= ? 
      AND c.experience GLOB '*[A-Za-z]*'
    GROUP BY c.candidate_name, c.job_title, c.email, c.phone_number
    ORDER BY match_score DESC
    """
    df = pd.read_sql_query(query, conn, params=(job_title, min_score))
    conn.close()
    return df

def generate_email_preview(candidate_name, job_title):
    interview_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
    recruiter_email = "sdhage@gmail.com"
    recruiter_phone = "+1-123-456-7890"
    recruiter_name = "Shruti Dhage"
	
    email_preview = f"""
    Subject: Interview Invitation for {selected_candidate['candidate_name']} for {selected_candidate['job_title']} Role

    Dear {selected_candidate['candidate_name']},

    Congratulations! Based on your application and profile evaluation, we are pleased to invite you for an interview for the {job_title}.
    Please confirm whether below details are correct.
        🎓 Education: {selected_candidate['education']}
        💼 Experience: {selected_candidate['experience']}
        🛠 Skills: {selected_candidate['skills']}

    Proposed Date & Time: {interview_date}
	📃 Interview Details:
    📅 Date & Time: {interview_date}
    📍 Mode: Virtual / In-Person (TBD)
    
	
	Please confirm your availability by replying to this email or contacting:
        📧 {recruiter_email}  |  📞 {recruiter_phone}
        
    Looking forward to hearing from you!  

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
    #shortlisted_df = pd.dataframe(shortlisted_df)
    if not shortlisted_df.empty:
        
        display_df=shortlisted_df.drop(columns=['email','phone_number'],errors='ignore')
        st.write(display_df)
        
        selected_index = st.selectbox(
        "Select a Candidate",
        display_df.index,
        format_func=lambda x: f"{display_df.loc[x, 'candidate_name']} ({display_df.loc[x, 'match_score']:.2f})"
    )

         # Fetch full details from original DataFrame
        selected_candidate = shortlisted_df.iloc[selected_index].to_dict()  # Full candidate details as dict

        # Display selected candidate's full details
        st.subheader("Selected Candidate Details")
        st.write(selected_candidate)  # Show full candidate data in readable format

        # Show Email Preview
        st.subheader("Email Preview")
        email_preview = generate_email_preview(selected_candidate, selected_job)
        st.text(email_preview)

        # Send Email Button
        if st.button(f"Send Email to {selected_candidate['candidate_name']}"):
            st.success(f"Email sent successfully to {selected_candidate['candidate_name']}!")

       
    else:
        st.warning("No candidates meet the match criteria.")