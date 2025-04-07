import random
import json
from faker import Faker

from similarity import job_title_similarity_sbert

# Load the job to skills map and education-job map from generated files
with open('final/job_skill_map.json', 'r') as f:
    job_skill_map = json.load(f)

with open('final/education_job_map.json', 'r') as f:
    education_job_map = json.load(f)

# Initialize Faker
fake = Faker()
Faker.seed(42)

# Function to generate a resume based on selected education and job titles
def generate_resume():
    # Randomly select a college major (education)
    education = random.choice(list(education_job_map.keys()))
    possible_jobs = education_job_map[education]
    
    num_jobs = random.randint(1, 3)
    experience = []
    last_end = 2025

    for _ in range(num_jobs):
        start = last_end - random.randint(1, 3)
        end = last_end
        last_end = start

        # Pick a random job from the jobs related to the selected education
        job_title = random.choice(possible_jobs)

        # Get the skills for that job from job_skill_map
        job_skills = job_skill_map.get(job_title, [])

        # Pick a subset of skills for the job experience
        num_skills = random.randint(3, 6)
        skills = random.sample(job_skills, min(num_skills, len(job_skills)))

        experience.append({
            "title": job_title,
            "company": fake.company(),
            "start_year": start,
            "end_year": end,
            "skills": skills
        })

    # Gather all skills for the resume (unique skills across all jobs)
    resume_skills = list({skill for job in experience for skill in job["skills"]})

    return {
        "name": fake.name(),
        "email": fake.email(),
        "education": education,
        "skills": resume_skills,
        "experience": experience
    }

# Function to generate a job posting
def generate_job_posting():
    education = random.choice(list(education_job_map.keys()))
    associated_jobs = education_job_map.get(education, [])

    # Pick a random job title from the associated jobs
    job_title = random.choice(associated_jobs)
    available_skills = job_skill_map.get(job_title, [])

    # Ensure the sample size doesn't exceed the number of available skills
    num_required_skills = min(4, len(available_skills))
    required_skills = random.sample(available_skills, num_required_skills)

    # Return the job posting with the title, required skills, experience, and education
    return {
        "title": job_title,
        "required_skills": required_skills,
        "minimum_experience": random.randint(2, 6),
        "required_education": education
    }

def compute_match_label(resume, job):
    # Avoid division by zero by checking if required_skills is empty
    if not job["required_skills"]:
        return 1.0  # TODO: What should a skill-less job be labeled? 1.0 or 0.0? 

    # Skill matching score
    skills_match = len(set(job["required_skills"]).intersection(set(resume["skills"]))) / len(job["required_skills"])

    # Job Title Similarity: Calculate similarity for all job titles in the resume against the job posting title
    job_titles_in_resume = [experience["title"] for experience in resume["experience"]]
    job_title_similarities = [job_title_similarity_sbert(title, job["title"]) for title in job_titles_in_resume]
    
    # If there are job titles in the resume, average the similarity score; else, assume no match
    job_title_similarity = sum(job_title_similarities) / len(job_title_similarities) if job_title_similarities else 0

    # Experience score: Calculate the total years of experience and normalize against the required experience
    years_experience = sum([job["end_year"] - job["start_year"] for job in resume["experience"]])
    experience_score = min(years_experience / job["minimum_experience"], 1)

    # Education match bump: Check if resume education matches required job education
    education_match = 1 if resume["education"] == job["required_education"] else 0

    # Weighted average of skills match, experience score, job title similarity, and education match
    match_label = round(0.20 * skills_match + 0.15 * experience_score + 0.60 * job_title_similarity + 0.05 * education_match, 2)

    return match_label


# Function to generate the labeled dataset
def generate_labeled_dataset(n=1000):
    dataset = []
    for _ in range(n):
        resume = generate_resume()
        job = generate_job_posting()
        label = compute_match_label(resume, job)
        dataset.append({
            "resume": resume,
            "job": job,
            "label": label
        })
    return dataset

# # Example: Generate a dataset of 1000 samples
# dataset = generate_labeled_dataset(n=1000)

# # Save the dataset to a JSON file
# with open('generated_dataset.json', 'w') as f:
#     json.dump(dataset, f, indent=4)

# print("Generated dataset with", len(dataset), "samples saved to 'generated_dataset.json'.")
