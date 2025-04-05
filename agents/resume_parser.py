import os
import sqlite3
import ollama
import json
import subprocess
import fitz  # PyMuPDF for PDF extraction

# Define the path to the resume folder
RESUME_FOLDER = r"C:\Users\shruti_dhage\Desktop\HackTheFuture\multiagent-job-screening\Inputs\CVs1"
model_name = "mistral"  # Replace with your actual model name
ollama_executable = r"C:\Users\shruti_dhage\AppData\Local\Programs\Ollama\ollama.exe"

# Function to extract text from PDF resumes
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text.strip()

# Function to parse resumes using LLM
def parse_resume_with_llm(resume_text):
    prompt = f"""
    You are an expert resume parser. Extract the following details from the given resume, Do not halucinate, if any of the data is missing  insert "Unknown".
    Job_title should not be NULL, it could be something containing developer, engineer etc. It can be usually found under project or work experience section.
    Provide the response in JSON format with columns. The output should be only strings, if there are multiple values for any of the column separate it by ",". 
    "candidate_name","email","phone_number","job_title","education","Projects", "experience","skills","certification"

    Resume Content:
    {resume_text}
    """

    try:
        # Call the Ollama CLI using subprocess
        process = subprocess.run(
            [ollama_executable, "run", model_name, prompt],
            capture_output=True,
            text=True,
            check=True
        )
        # Expecting a JSON string from the model output
        print(repr(process.stdout.strip()))
        cleaned_output = process.stdout.strip()
        cleaned_output = cleaned_output.replace("NULL", "null") 
        cleaned_output = cleaned_output.encode('utf-8').decode('utf-8') 
        parsed_data =  json.loads(cleaned_output)
    except subprocess.CalledProcessError as e:
        parsed_data = {"error": f"Ollama call failed: {e}"}
    except json.JSONDecodeError as e:
        parsed_data = {"error": f"JSON decoding error: {e}"}
    
    # Add the job title to the summary
    return parsed_data

    # Function to insert candidate data into SQLite
def insert_candidate_data(candidate_data):
    conn = sqlite3.connect("job_screening.db")
    cursor = conn.cursor()

    columns = ["candidate_name", "email", "phone_number", "job_title" ,"education", "Projects", "experience", "skills", "certification"]

    # Ensure all values are either strings or empty strings if None
    values = []
    for col in columns:
        value = candidate_data.get(col, "")  # Default to empty string if missing
        if isinstance(value, list):  # Convert list to comma-separated string
            print(value)
            value = ", ".join(value)
        
        values.append(value)

    sql = """
    INSERT INTO candidate_data (candidate_name, email, phone_number, "job_title",education, Projects, experience, skills, certification)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        with conn:
            conn.execute(sql, tuple(values))
        print(f"✅ Candidate '{values[0]}' inserted successfully!")
        rows=conn.execute("""select * from candidate_data""")
        for row in rows:
            print(row)
    except Exception as e:
        print(f"❌ Error inserting candidate data: {e}")
    conn.close()

# Main execution
if __name__ == "__main__":
    resumes = {}
    for filename in os.listdir(RESUME_FOLDER):
        if filename.endswith(".pdf"):  # Assuming resumes are in PDF format
            pdf_path = os.path.join(RESUME_FOLDER, filename)
            resume_text = extract_text_from_pdf(pdf_path)
            parsed_data = parse_resume_with_llm(resume_text)
        if parsed_data:
            insert_candidate_data(parsed_data)
            print(f"✅ Successfully stored candidate data for {filename}")
        else:
            print(f"❌ Failed to parse resume: {filename}")
