import subprocess
import json
import ollama
import csv
import sys
import os

# Get the parent directory of the current file (agent folder) so we can access the core folder
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
from core.insert_jd import *
def summarize_jd_list(jd_list: list) -> list:
    """
    Receives a list of dictionaries, each containing:
      - "Job_title": the job title.
      - "job description": the job description text.
    
    For each dictionary, the function calls the Ollama-based LLM to extract key elements
    from the job description and then adds the job title to the summary.
    
    Returns:
      A JSON-formatted string containing a list of dictionaries. Each dictionary has the keys:
        - "job_title"
        - "required_skills"
        - "experience"
        - "qualifications"
        - "responsibilities"
      (or an "error" key in case of failure)
    """
        # Build the prompt that will instruct the model what to do.
    # Specify your model name as configured in your Ollama installation.
    model_name = "mistral"  # Replace with your actual model name
    # It is assumed that 'ollama' is in your system PATH.
    ollama_executable = r"C:\Users\shruti_dhage\AppData\Local\Programs\Ollama\ollama.exe"
    results=[]
    print(jd_list)

    for job in jd_list:
        job_title = job.get("job_title", "").strip()
        job_description = job.get("job_description", "").strip()
        
        # Build the prompt for the LLM
        prompt = (
            f"""Extract the key elements from the job description .
            "Identify required skills, years of experience, educational qualifications, "
            "and key responsibilities. Return the output in JSON format with keys: "
            "'required_skills', 'experience', 'qualifications', 'responsibilities'.\n\n"
             Job Description: {job_description}
            The output should be only strings, if there are multiple values for any of the column separate it by ","."""
        )
        
        try:
            # Call the Ollama CLI using subprocess
            process = subprocess.run(
                [ollama_executable, "run", model_name, prompt],
                capture_output=True,
                text=True,
                check=True
            )
            # Expecting a JSON string from the model output
            summary = json.loads(process.stdout.strip())
        except subprocess.CalledProcessError as e:
            summary = {"error": f"Ollama call failed: {e}"}
        except json.JSONDecodeError as e:
            summary = {"error": f"JSON decoding error: {e}"}
        
        # Add the job title to the summary
        print(type(summary))
        summary["job_title"] = job_title
        results.append(summary)
        print(results)
    
    # Return the complete list as a formatted JSON string
    return results
        

def read_job_descriptions(file_path: str) -> list:
    """
        Reads a CSV file containing job descriptions with headers that may include spaces.
        We override the CSV headers with our own standardized field names.
        
        Parameters:
            file_path (str): The path to the CSV file.
        
        Returns:
            list: A list of dictionaries, each with keys 'job_title' and 'job_description'.
        """
    job_list = []
    with open(file_path, mode="r", encoding="utf-8", newline="",errors="ignore") as csvfile:
        # Override the header using the fieldnames parameter
        # The file header might be like "job title" and "job description"
        reader = csv.DictReader(csvfile, fieldnames=["Job Title", "Job Description"])
        # Skip the first row (actual header row in file)
        next(reader)
        for row in reader:
            job_list.append({
                "job_title": row.get("Job Title", "").strip(),
                "job_description": row.get("Job Description", "").strip()
            })
        #print("job_list:",job_list)
        return job_list

if __name__ == "__main__":
    # Path to your file containing JDs
    file_path = r"C:\Users\shruti_dhage\Desktop\HackTheFuture\multiagent-job-screening\Inputs\job_description.csv"  
    jobs = read_job_descriptions(file_path) #returns list of dict
    results = summarize_jd_list(jobs)
    connection = create_connection()
    create_table(connection)
    insert_job_data(connection, jobs=results)
    connection.close()

        
        
    
    
