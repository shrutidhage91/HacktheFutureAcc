import subprocess
import json
import ollama
import csv
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
    with open(file_path, mode="r", encoding="utf-8", newline="") as csvfile:
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
        print("job_list:",job_list)
        return job_list

if __name__ == "__main__":
    # Path to your file containing JDs
    file_path = r"C:\Users\shruti_dhage\Desktop\HackTheFuture\multiagent-job-screening\Inputs\job_description.csv"  
    jobs = read_job_descriptions(file_path)
    for idx, job in enumerate(jobs, start=1):
        print(f"Job {idx}: {job['job_title']}")
        print("Description:")
        print(job['job_description'])
        print("\n" + "=" * 40 + "\n")