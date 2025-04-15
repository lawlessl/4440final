import subprocess
import json
import csv
import os
import time

def parse_resume(file_name, pdf_path):
    # Command to run the TypeScript parser
    command = ["npx", "ts-node", "/Users/liamlawless/Desktop/Northeastern/2024-2025 School Year/DS4440/4440final/parser/lib/run.ts", pdf_path]
    output_dir = "/Users/liamlawless/Desktop/Northeastern/2024-2025 School Year/DS4440/4440final/parser/parsed_resumes"

    try:
        # Run the TS script
        subprocess.run(command, check=True, capture_output=True, text=True)

        # Wait for the JSON file to exist (in case it's written slightly after subprocess ends)
        timeout = 5  # seconds
        f_path = f"{output_dir}/{file_name}.json"
        start_time = time.time()
        while not os.path.exists(f_path):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out waiting for JSON file: {f_path}")
            time.sleep(0.2)  # wait a bit and check again

        # Now load the JSON data
        with open(f_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)

            first_experience_descriptions = resume_data['workExperiences'][0]['descriptions']
            first_experience_title = resume_data['workExperiences'][0]['jobTitle']
            applicant_skills = resume_data['skills']['descriptions']
            applicant_skill = ' '.join(applicant_skills)

            result = {
                "applicant_job_role": first_experience_title,
                "applicant_experience": first_experience_descriptions,
                "applicant_skills": applicant_skill
            }

            return result

    except subprocess.CalledProcessError as e:
        print("Error while running TS parser:\n", e.stderr)
    except Exception as e:
        print("Unexpected error:\n", str(e))
