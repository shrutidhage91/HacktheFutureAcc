from datetime import datetime, timedelta

def schedule_interviews(shortlisted_candidates, recruiter_email, recruiter_phone):
    interview_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")

    for candidate in shortlisted_candidates:
        email_content = f"""
        Subject: Interview Invitation for {candidate['candidate_name']}
        
        Dear {candidate['candidate_name']},
        Congratulations! Based on your application and profile evaluation, we are pleased to invite you for an interview for the {candidate['job_title']}.

        **Interview Details:**
        📅 Date & Time: {interview_date}
        📍 Mode: Virtual / In-Person (TBD)
        
       Please confirm whether below details are correct.
        🎓 Education: {candidate['education']}
        💼 Experience: {candidate['experience']}
        🛠 Skills: {candidate['skills']}
        

        Please confirm your availability by replying to this email or contacting:
        📧 {recruiter_email}  |  📞 {recruiter_phone}
        
        Looking forward to hearing from you!
        

        Best regards,  
        Recruitment Team
        """

        print(f"Dry Run Email to {candidate['email']}:\n{email_content}\n{'-'*80}")

# Example usage
if __name__ == "__main__":
    from shortlist_candidate import shortlist_candidates

    job_title = "Data Scientist"
    min_match_score = 0.70
    recruiter_email = "recruiter@example.com"
    recruiter_phone = "+1-123-456-7890"

    shortlisted_candidates = shortlist_candidates(job_title, min_match_score)
    schedule_interviews(shortlisted_candidates, recruiter_email, recruiter_phone)
