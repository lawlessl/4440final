import json
from sentence_transformers import SentenceTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from mock_data import generate_job_posting, generate_resume
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

# Load the job match JSON from generated files
with open('4440final/job_match.json', 'r') as f:
    job_match = json.load(f)

def resume_to_text(resume):
    exp_str = "\n".join([f"{e['title']} at {e['company']} ({e['start_year']}-{e['end_year']})" for e in resume["experience"]])
    skills = ", ".join(resume["skills"])
    return f"{resume['education']}\nSkills: {skills}\nExperience:\n{exp_str}"

def job_to_text(job):
    skills = ", ".join(job["required_skills"])
    return f"{job['title']}\nRequired Skills: {skills}\nExperience: {job['minimum_experience']} years\nEducation: {job['required_education']}"

def prepare_dataset(data):
    resume_texts = [resume_to_text(d["resume"]) for d in data]
    job_texts = [job_to_text(d["job"]) for d in data]
    pairs = [r + "\n\n" + j for r, j in zip(resume_texts, job_texts)]
    embeddings = model.encode(pairs)
    labels = [d["label"] for d in data]
    return np.array(embeddings), np.array(labels)

X, y = prepare_dataset(job_match)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

regressor = RandomForestRegressor()
regressor.fit(X_train, y_train)

preds = regressor.predict(X_test)
print("RMSE:", root_mean_squared_error(y_test, preds))




def detect_risks(resume):
    risks = []
    exp = sorted(resume["experience"], key=lambda x: x["start_year"])
    for i in range(1, len(exp)):
        gap = exp[i]["start_year"] - exp[i-1]["end_year"]
        if gap > 1:
            risks.append(f"Employment gap of {gap} years between {exp[i-1]['company']} and {exp[i]['company']}")
    if len(exp) >= 3 and all((exp[i]["end_year"] - exp[i]["start_year"]) <= 1 for i in range(len(exp))):
        risks.append("Frequent job-hopping detected")
    return risks



def evaluate_candidate(resume, job):
    combined = resume_to_text(resume) + "\n\n" + job_to_text(job)
    embedding = model.encode([combined])
    score = regressor.predict(embedding)[0]
    risks = detect_risks(resume)
    return {
        "fit_score": round(score, 2),
        "risk_flags": risks
    }

# resume = generate_resume()
# job = generate_job_posting()

job = {
  "title": "Hydroelectric Plant Technician",
  "required_skills": ["Equipment Maintenance", "Operation Monitoring", "Mechanical Knowledge", "Critical Thinking"],
  "minimum_experience": 4,
  "required_education": "Engineering"
}

resume = {
  "name": "Kendra Patel",
  "email": "kendrapatel92@example.org",
  "education": "Mechanical Engineering",
  "skills": ["Operation Monitoring", "Mechanical Knowledge", "Equipment Maintenance", "Critical Thinking", "Troubleshooting", "Monitoring", "Coordination", "Repairing"],
  "experience": [
    {
      "title": "Power Plant Operator",
      "company": "EverGreen Energy Systems",
      "start_year": 2021,
      "end_year": 2025,
      "skills": ["Operation Monitoring", "Mechanical Knowledge", "Repairing"]
    },
    {
      "title": "Industrial Machinery Mechanic",
      "company": "Nexus HydroTech",
      "start_year": 2018,
      "end_year": 2021,
      "skills": ["Equipment Maintenance", "Troubleshooting", "Critical Thinking", "Coordination"]
    },
    {
      "title": "Maintenance Technician",
      "company": "Cascade Utilities Corp.",
      "start_year": 2016,
      "end_year": 2018,
      "skills": ["Repairing", "Monitoring", "Mechanical Knowledge"]
    }
  ]
}


print(job, '\n\n', resume)

result = evaluate_candidate(resume, job)
print(json.dumps(result, indent=2))