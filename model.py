import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from transformers import BertModel, BertTokenizer
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from builtins import round
import pandas as pd

def predict_suitability(model, tokenizer, jd_text, resume_text, device):
    model.eval()

    encoding = tokenizer(
        jd_text, resume_text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=512
    )

    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        output = model(input_ids=input_ids, attention_mask=attention_mask)

    return output.item()


# Make the model
class JobFitModel(nn.Module):
    def __init__(self):
        super(JobFitModel, self).__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.ffn = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )


    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_embedding = outputs.last_hidden_state[:, 0, :]  # Grab [CLS] token
        score = self.ffn(cls_embedding)
        return score.squeeze(1)  # Return shape: (batch_size,)

def get_uploaded_match_scores():
    # Load the bert tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    title_model = JobFitModel()
    skills_model = JobFitModel()
    resp_model = JobFitModel()

    title_model.load_state_dict(torch.load("title_model.pt", map_location=device))
    skills_model.load_state_dict(torch.load("skills_model.pt", map_location=device))
    resp_model.load_state_dict(torch.load("resp_model.pt", map_location=device))

    title_model.to(device).eval()
    skills_model.to(device).eval()
    resp_model.to(device).eval()


    # Load your CSV
    df = pd.read_csv("combined_data.csv")
    df.columns = df.columns.str.strip()

    # Create empty columns to store scores
    df["Title Match Score"] = 0.0
    df["Skills Match Score"] = 0.0
    df["Responsibilities Match Score"] = 0.0
    df["Overall Suitability Score"] = 0.0

    # Loop through each row and compute scores
    for i, row in df.iterrows():
        job_title = str(row["job_role"])
        job_skills = str(row["job_skills"])
        job_responsibilities = str(row["job_responsibilities"])
        job_description = str(row["job_description"])

        resume_role = str(row["applicant_job_role"])
        resume_skills = str(row["applicant_skills"])
        resume_experience = str(row["applicant_experience"])

        responsibilities_input = job_responsibilities + " " + job_description

        title_score = predict_suitability(title_model, tokenizer, job_title, resume_role, device)
        skills_score = predict_suitability(skills_model, tokenizer, job_skills, resume_skills, device)
        resp_score = predict_suitability(resp_model, tokenizer, responsibilities_input, resume_experience, device)

        df.at[i, "Title Match Score"] = title_score
        df.at[i, "Skills Match Score"] = skills_score
        df.at[i, "Responsibilities Match Score"] = resp_score
        df.at[i, "Overall Suitability Score"] = round((0.25 * title_score) + (0.33 * skills_score) + (0.37 * resp_score), 4)

    return df