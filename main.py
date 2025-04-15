from parser.parse_resume import parse_resume
import os
import csv

def main():
    directory = 'resumes/'
    job_description = {
        "job_role": "Software Engineer",
        "job_description": "We are looking for a Software Engineer to design, develop, and maintain scalable web applications. You’ll work closely with product and design teams to deliver high-quality features and improve performance across the stack. Ideal candidates are proficient in modern JavaScript frameworks, backend APIs, and have experience working in agile environments. Strong problem-solving skills and a passion for clean, maintainable code are essential.",
        "job_skills": "HTML, CSS, JavaScript Frontend frameworks (e.g., React, Angular) User experience (UX)RESTful APIs Version control (Git)",
        "job_responsibilities": "Design and implement responsive user interfaces using modern frontend frameworks. Work with backend APIs to deliver seamless user experiences and ensure high application performance.",
    }
    parsed_resumes = []

    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            file_path = os.path.join(directory, filename)
            file_name = os.path.basename(file_path)
            # Remove the .pdf extension
            file_name = os.path.splitext(file_name)[0]

            res = parse_resume(file_name, file_path)
            parsed_resumes.append(res)

    # Combine parsed resumes with job description
    combined_data = []
    for resume in parsed_resumes:
        combined_data.append({**resume, **job_description})

    # Save combined data as a CSV file
    output_file = 'combined_data.csv'
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=combined_data[0].keys())
        writer.writeheader()
        writer.writerows(combined_data)

    print(f"Combined data saved as {output_file}")

if __name__ == "__main__":
    main()

