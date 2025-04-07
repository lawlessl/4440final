import csv
from collections import defaultdict
import inflect  # To convert plural job titles to singular

# Path to O*NET data files
ONET_DIR = "4440final"

# Filenames inside the O*NET directory
occupation_file = f"{ONET_DIR}/Occupation_Data.txt"
skills_file = f"{ONET_DIR}/Skills.txt"

# Initialize inflect engine
p = inflect.engine()

def load_occupation_titles():
    """Returns SOC_Code -> Job Title"""
    soc_to_title = {}
    with open(occupation_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            soc_to_title[row["O*NET-SOC Code"]] = row["Title"]
    return soc_to_title

def load_skills():
    """Returns SOC_Code -> List of (Skill, Importance Rating)"""
    soc_to_skills = defaultdict(list)
    with open(skills_file, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            soc_code = row["O*NET-SOC Code"]
            skill_id = row["Element ID"]
            skill_name = row["Element Name"]
            importance = float(row["Data Value"]) if row["Scale ID"] == "IM" else 0.0  # Only importance scale
            soc_to_skills[soc_code].append((skill_name, importance))
    return soc_to_skills

def build_job_to_skills(top_n=10, min_importance=3.0):
    soc_to_title = load_occupation_titles()
    soc_to_skills = load_skills()

    job_to_skills = {}

    # Map SOC code to job titles and associated skills
    for soc_code, skills in soc_to_skills.items():
        job_title = soc_to_title.get(soc_code)
        if job_title:
            # Convert job title to singular form
            singular_job_title = p.singular_noun(job_title) or job_title  # Use inflect to convert plural to singular

            # Filter and sort skills based on importance
            sorted_skills = sorted(skills, key=lambda x: x[1], reverse=True)
            filtered_skills = [skill for skill, importance in sorted_skills if importance >= min_importance]
            job_to_skills[singular_job_title] = filtered_skills[:top_n]

    return job_to_skills

if __name__ == "__main__":
    job_skill_map = build_job_to_skills()

    # Save the job-to-skills mapping to a JSON file
    import json
    with open("job_skill_map.json", "w") as f:
        json.dump(job_skill_map, f, indent=2)

    print("Job-to-skills mapping saved to job_skill_map.json")
    print("Sample:", list(job_skill_map.items())[:3])
